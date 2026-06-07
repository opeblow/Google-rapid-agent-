# Deployment Guide

How to deploy WC2026 Agent: the **backend** (unified FastAPI app) on **Render** and the **frontend** (React/Vite SPA) on **Vercel**, talking to **MongoDB Atlas**.

```
  Vercel (React SPA)  ──HTTPS──>  Render (FastAPI + in-process agent)  ──>  MongoDB Atlas
                                   └─ Gemini via OpenRouter
                                   └─ MongoDB MCP Server (read-only, via npx)
```

Since the merge, the agent runs **in-process inside the backend** — there is only one service to deploy, not two.

---

## Prerequisites

- **MongoDB Atlas** cluster + connection string (`mongodb+srv://…`).
  - Atlas → **Network Access** → allow `0.0.0.0/0` (Render's outbound IPs are dynamic).
- **OpenRouter** API key (https://openrouter.ai/keys).
- GitHub repo connected to Render and Vercel.
- The branch you're deploying (e.g. `main` after merging `unify-app`).

---

## 1. Backend → Render (Docker)

The agent's MongoDB MCP integration shells out to `npx mongodb-mcp-server`, so the runtime needs **Node.js**. The repo's root `Dockerfile` already installs both Python and Node, so deploy it as a **Docker** service (not the native Python runtime — that has no Node, and MCP would silently fall back to the custom tools only).

### Create the service
1. Render → **New** → **Web Service** → connect the repo.
2. **Runtime:** Docker. **Dockerfile path:** `./Dockerfile` (repo root). Leave Root Directory blank.
3. **Instance type:** any (Free works for a demo; note free instances cold-start).
4. **Health check path:** `/api/health`

### Environment variables
| Key | Value | Notes |
|-----|-------|-------|
| `OPENROUTER_API_KEY` | `sk-or-v1-…` | required (secret) |
| `MONGODB_URI` | `mongodb+srv://…` | required (secret) |
| `DATABASE_NAME` | `worldcup_2026` | |
| `OPENROUTER_MODEL` | `google/gemini-3-flash-preview` | optional (this is the default) |

> **Do NOT set `MOUNT_FRONTEND`.** Leaving it unset keeps the backend API-only; the SPA is served by Vercel. (Setting it to `true` would make the backend serve a bundled SPA and shadow `/api` — only use that for an all-in-one single-service deploy.)

`PORT` is provided by Render automatically; the container's `start_hf.py` reads it and binds `0.0.0.0:$PORT`.

### What happens on boot
`start_hf.py` runs `seed.py` (idempotent upsert of the 72 real group-stage fixtures) and then launches `uvicorn server:app`. The agent + read-only MCP bridge initialize in the app's lifespan. No manual seeding needed.

### Verify
```bash
curl https://<your-service>.onrender.com/api/health
# {"status":"ok","agent":"ready","database":"connected","provider":"openrouter",
#  "model":"google/gemini-3-flash-preview","llm":"connected","mcp":"enabled (16 tools)", ...}
```
- `mcp: "enabled (N tools)"` → MCP bridge is up (Node present). If it says `disabled`, the runtime lacks Node — confirm you used the Docker runtime.
- **Copy this service URL** — the frontend needs it.

> **Optional (faster MCP cold start):** add `RUN npm install -g mongodb-mcp-server` to the runtime stage of the `Dockerfile` so `npx` doesn't download it on first request (the bridge has a 30s init timeout and otherwise falls back to custom tools on a slow cold start).

---

## 2. Frontend → Vercel

1. Vercel → **Add New** → **Project** → import the repo.
2. **Root Directory:** `frontend`  ← important (the app lives in `frontend/`).
3. **Framework Preset:** Vite (auto-detected). Build = `npm run build`, Output = `dist` (defaults are fine).
4. SPA routing is handled by `frontend/vercel.json` (rewrites every path to `/index.html`).

### Environment variables (Project → Settings → Environment Variables)
| Key | Value | Why |
|-----|-------|-----|
| `VITE_API_URL` | `https://<your-render-service>.onrender.com` | the frontend calls this for `/api/*`. Without it, `api.js` falls back to a hardcoded production URL. |
| `VITE_BASE` | `/` | the app is served at the domain root on Vercel. The default base is the GitHub-Pages sub-path, which would break on Vercel. |

These are **build-time** variables (Vite inlines them), so set them **before** the first deploy (or redeploy after adding).

### Verify
- Open the Vercel URL → the landing page renders ("THE WORLD'S GAME. YOUR TRIP.").
- Click **Start Planning** → complete onboarding → a plan generates with **real** fixtures.
- DevTools → Network: `/api/chat` should hit your Render URL and return `200`.

---

## 3. CORS

The backend sets `allow_origins=["*"]`, so the Vercel domain can call it out of the box. To lock it down later, replace `"*"` in `backend/server.py` (the `CORSMiddleware`) with your Vercel domain.

---

## Troubleshooting

| Symptom | Cause / Fix |
|---|---|
| Frontend loads but body is blank (navbar/footer only) | `VITE_BASE` not set to `/` on Vercel → router basename mismatch. Set it and redeploy. |
| Chat hits the wrong backend / CORS errors | `VITE_API_URL` missing or wrong on Vercel (it's falling back to the hardcoded URL in `api.js`). |
| `/api/health` shows `mcp: "disabled"` | Runtime has no Node → use the **Docker** runtime on Render. |
| `/api/health` shows `database: "disconnected"` | Atlas IP allowlist missing `0.0.0.0/0`, or wrong `MONGODB_URI`. |
| Plans empty / agent error | Bad/at-quota `OPENROUTER_API_KEY`. |
| Backend returns the SPA instead of JSON on `/` | `MOUNT_FRONTEND` is set — unset it for the split deploy. |

---

## Local development (recap)

```bash
# backend (port 8002)
cd backend && ../.venv/bin/python -m uvicorn server:app --host 127.0.0.1 --port 8002
# frontend (port 5173/5174) — create frontend/.env.local with VITE_API_URL=http://localhost:8002
cd frontend && npm run dev
```
Root `.env` holds `OPENROUTER_API_KEY`, `MONGODB_URI`, `DATABASE_NAME` for the backend. Seed real fixtures with `cd backend && python seed.py` (idempotent).

---

## Alternative: all-in-one (single service)

To serve the SPA from the backend instead of Vercel (one Render service, no Vercel): build the frontend (`npm run build` with `VITE_BASE=/`), set `MOUNT_FRONTEND=true` on Render, and the Docker image will serve the SPA at `/` with the API under `/api`. The repo's `render.yaml` is a blueprint along these lines.
