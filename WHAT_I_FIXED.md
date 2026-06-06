# What I Fixed

A log of the changes made on the `unify-app` branch, why they were needed, and how each was verified.

---

## 1. Switched the LLM provider to OpenRouter (Gemini 3 Flash)

**Why:** The direct Google AI Studio key returned `429 RESOURCE_EXHAUSTED` (free-tier quota `limit: 0`) and enabling billing was painful.

**What:**
- Replaced the `google-genai` SDK with the OpenAI-compatible **OpenRouter** client (`AsyncOpenAI`), model **`google/gemini-3-flash-preview`**.
- Rewrote the function-calling loop into OpenAI tool-calling format (system/user/assistant/tool messages).
- **Gemini 3 gotcha handled:** Gemini 3 returns encrypted "thought signatures" (`reasoning_details`) with each tool call and *requires them to be echoed back* on the next turn, or multi-turn function calling breaks. The loop now preserves and re-sends them.

**Files:** `backend/agent.py`, `backend/config.py`, `backend/requirements.txt` (`openai` replaces `google-genai`), `.env`.

**Config:** `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, `OPENROUTER_BASE_URL`.

---

## 2. Dashboard never showed the generated plan (state hand-off bug)

**Symptom:** After the onboarding wizard → "Generate Plan", the dashboard opened with an **empty chat** and **"No matches yet"**, even though Budget/Travelers carried over.

**Root cause:** The plan *was* generated and saved (it was in MongoDB), but the frontend threw the result away:
- `OnboardingWizard.handleGenerate()` discarded the agent's response (`reply`, `plan_data`) and stored only the onboarding *inputs* in `localStorage`.
- The dashboard / `ChatInterface` never re-fetched the session. The helpers built for exactly this — `getSessionHistory()` and `getPlan()` in `api.js` — existed but were **never called** (dead code).

**Fix:** `ChatInterface` now hydrates from the session on mount — fetches `getSessionHistory(sessionId)`, restores the conversation, and pushes the latest `plan_data` to the itinerary panel via `onPlanUpdate`. This is refresh-safe and also works when reopening a plan from "My Plans".

**Files:** `frontend/src/components/ChatInterface.jsx`.

---

## 3. Merged the two backend services into one FastAPI app

**Why:** The `agent` (`:8001`) and `backend` (`:8000`) ran as two separate processes that shared **one database** (and both wrote the `plans` collection). The backend just proxied chat to the agent over `httpx` — an extra network hop, duplicate scaffolding (`db.py`/`config.py` ×2), and port-collision pain, for benefits the project wasn't using.

**What:**
- Agent logic moved **in-process**: `/api/chat` now calls `process_message()` directly — no HTTP, no 60 s proxy timeout.
- Deleted the `agent/` directory; moved `tools.py`, `mcp_bridge.py`, `seed.py` into `backend/`; refactored `agent_server.py` into the library module **`backend/agent.py`** (`init_agent` / `process_message` / `close_agent` / `agent_status`).
- Unified `config.py`; updated deploy files (`start_hf.py`, `Dockerfile`, `render.yaml`) to a single service.

**Result:** one process, one port, **~186 fewer lines**. Health/MCP/tool-calling all verified identical to the two-service version.

**Files:** `backend/agent.py` (new), `backend/server.py`, `backend/config.py`, `backend/requirements.txt`, `start_hf.py`, `Dockerfile`, `render.yaml`; `agent/` removed.

---

## 4. Plans were shallow and didn't render (schema-contract gap)

**Symptom:** Even after the hydration fix, the itinerary tabs were broken — Matches showed "undefined vs undefined", Hotels/Daily Plan were empty, Budget showed placeholder values.

**Root cause:** `save_plan` accepted a **free-form** `plan_data` dict and the system prompt never pinned a structure, so Gemini emitted a different, partial shape on every call — one that didn't match the field names each UI component reads (`hotel` object vs `hotels[]`, `"A vs B"` string vs `home_team`/`away_team`, scalar `budget` vs `categories[]`, no `days[]`).

**Fix:**
- **Pinned `SAVE_PLAN_SCHEMA`** to the exact structure the UI renders: `matches[]` (`home_team`, `away_team`, `date`, `time`, `venue`, `city`, `country`, `stage`), `hotels[]` (`name`, `location`, `stars`, `price_per_night`, `amenities[]`), `days[]` (`title`, `date`, `match`, `hotel`, `activities[]`), `budget` + `categories[]` (`label`, `amount`), `travelers`.
- **Defensive normalization in `save_plan()`** — coerces common deviations (`hotel`→`hotels[]`, `"A vs B"`→teams, alias-maps `daily_plan`→`days`, `{name,cost}`→`{label,amount}`) **and re-hydrates each match from the DB** so cards always show real, grounded data even when the model paraphrases.
- **Strengthened the system prompt** — search first, include *every* match, always `save_plan`, fill every section, keep the budget realistic.

**Files:** `backend/tools.py`, `backend/agent.py`.

---

## 5. The agent was corrupting its own source data (MCP write access)

**Symptom:** Plans surfaced impossible fixtures (e.g. "Argentina vs Algeria" at 02:00); the `matches` collection had grown from **48 → 72**.

**Root cause:** The MongoDB MCP bridge exposed **write** tools (insert/update/delete/drop) and the system prompt invited the model to "manipulate data directly". So while planning, Gemini injected/edited fixtures in the source-of-truth `matches` collection. `search_matches` then faithfully returned the corrupted data.

**Fix:**
- The MCP bridge now runs **read-only** (`--readOnly` + `MDB_MCP_READ_ONLY=true`) — write tools removed (**25 → 16** MCP tools). The agent can query but never mutate the database.
- `save_plan` is unaffected — it writes through the controlled custom tool (PyMongo), not raw MCP.
- Re-seeded a clean **48** matches to remove the injected/edited records.

**Files:** `backend/mcp_bridge.py`.

---

## Local run notes

- The app runs on **`:8002`** and the Vite dev server on **`:5174`** because ports `8000`/`5173` were occupied by another local project. `frontend/vite.config.js` proxy was pointed at `:8002`.
- Open **http://localhost:5174/Google-rapid-agent-/**.

## Verified end-to-end

A full Argentina request now produces a complete, grounded plan: **3 real matches** (vs Japan/Boston, vs Mexico/Houston, Mexico vs Argentina/Mexico City) · **3 hotels** · **7-day schedule** · **budget $6000 across 4 categories** · **2 travelers** — every dashboard tab populates.
