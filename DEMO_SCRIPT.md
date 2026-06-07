# Fanfare — 3-Minute Demo Script

> **Fanfare** — an AI agent that plans your entire 2026 FIFA World Cup trip in one conversation.
> Built for the Google Cloud Rapid Agent Hackathon (MongoDB track).

---

## Pre-flight (do this before you present)

- [ ] Backend up — `curl <backend>/api/health` returns `"status":"ok"` and `mcp: "enabled (...)"`.
- [ ] Frontend open on the **landing page**, browser zoomed so the split view is readable.
- [ ] **Warm it up:** generate one plan a few minutes before going live (cold starts + the first model call are the slowest). This also gives you a **fallback** — keep that dashboard URL in another tab in case the live run is slow.
- [ ] **Demo team = Brazil.** Real fixtures span three different cities (New York → Philadelphia → Miami), which makes a great "trip." Budget **$6,000**, **2** travelers. (Any seeded team works — Argentina, USA, Mexico, Spain, France, England… are all good.)

---

## The script (≈3:00)

### [0:00–0:20] · Hook
> **SAY:** "The 2026 World Cup is the biggest ever — 48 teams, 16 cities, three countries. For a fan trying to follow their team, planning the trip is a nightmare: which matches, which cities, hotels, budget. This is **Fanfare** — it plans your whole World Cup trip in a single chat."

**DO:** Show the landing page. Click **Start Planning**.

### [0:20–0:40] · Onboard (keep it quick)
> **SAY:** "I support Brazil, there are two of us, and our budget is six thousand dollars."

**DO:** Search & pick **Brazil** → Next → set budget **$6,000** + **2** travelers → Next → Next → **Generate My Plan**.

### [0:40–1:25] · Watch the agent work
> **SAY (while it generates):** "Fanfare is a Gemini agent. Right now it's calling tools — searching MongoDB for Brazil's *real* fixtures, then writing a complete, structured itinerary back into the database. This isn't a canned response; it's the model reasoning over live data."

**DO:** Land on the dashboard. The chat fills in with the itinerary narrative.

### [1:25–2:10] · The itinerary (click each tab)
> **SAY:** "And here's the plan — grounded in the real schedule."

**DO:** Walk the tabs on the right:
- **Matches** — "Brazil's actual group-stage matches: vs Morocco in New York, vs Haiti in Philadelphia, vs Scotland in Miami. Real venues, real dates, color-coded by country."
- **Daily Plan** — "A day-by-day schedule: arrival, match days, things to do in between."
- **Budget** — "Broken down by category and kept within budget."
- **Hotels** — "Recommended stays for each city."

### [2:10–2:40] · It's a conversation
**DO:** In the chat, type: **"Trim the budget to $4,000 and add a beach day in Miami — update my plan."** Send.
> **SAY:** "It's not a form — it's a conversation. I can refine anything in natural language and the itinerary updates live."

**DO:** Point at the updated reply / budget. *(Fallback: if it's slow, just click the **"Reduce budget to $3000"** suggestion chip.)*

### [2:40–3:00] · Tech + close
> **SAY:** "Under the hood: one FastAPI service with the agent running in-process, **Gemini via OpenRouter** for function-calling, and the **MongoDB MCP Server** giving the agent live, read-only access to the database — every match is real, straight from the 2026 draw, no hallucinations. That's **Fanfare**: your World Cup, planned in a chat."

---

## Talking points / likely questions

- **"Is the data real?"** — Yes. All 72 group-stage fixtures from the Dec 2025 final draw (real teams, venues, kickoff times). The agent can only *read* the database (MCP runs read-only), so it can't invent or corrupt fixtures.
- **MongoDB angle (the track):** MongoDB Atlas stores matches, plans, and chat sessions; the **MongoDB MCP Server** is the partner integration — it exposes the database to the Gemini agent as callable tools alongside Fanfare's own domain tools.
- **Architecture:** React/Vite SPA → one FastAPI backend (agent in-process, no extra hop) → MongoDB Atlas. Deployable on Vercel + Render (see `deployment.md`).
- **Why it won't embarrass you live:** the plan is regenerated each run, but it's always grounded in the seeded real fixtures — worst case it's a bit slow, never wrong.

## If something breaks
- Switch to the **pre-warmed dashboard tab** from pre-flight and narrate from there.
- Slow first response = cold start / first model call; mention it's warming up and keep talking.
