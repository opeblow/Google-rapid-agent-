# Deployment Guide

How to deploy WC2026 Agent: the **backend** (unified FastAPI app) on a cloud host and the **frontend** (React/Vite SPA), talking to **MongoDB Atlas**.

```
  Frontend (React SPA)  ──HTTPS──>  Backend (FastAPI + in-process agent)  ──>  MongoDB Atlas
                                     └─ Gemini via Google Generative AI SDK
                                     └─ MongoDB MCP Server (read-only, via npx)
```

Since the merge, the agent runs **in-process inside the backend** — there is only one service to deploy, not two.

---

## Prerequisites

- **MongoDB Atlas** cluster + connection string (`mongodb+srv://…`).
  - Atlas → **Network Access** → allow `0.0.0.0/0` (cloud hosts have dynamic IPs).
- **Google AI Studio** API key (https://aistudio.google.com/apikey).
- GitHub repo connected to your deploy platform.

---

## 1. Backend Deployment

The agent's MongoDB MCP integration shells out to `npx mongodb-mcp-server`, so the runtime needs **Node.js**. The repo's root `Dockerfile` already installs both Python and Node.

### Environment variables
| Key | Value | Notes |
|-----|-------|-------|
| `GOOGLE_API_KEY` | `AIza...` | required (secret) |
| `GEMINI_MODEL` | `gemini-3-flash-preview` | optional (this is the default) |
| `MONGODB_URI` | `mongodb+srv://…` | required (secret) |
| `DATABASE_NAME` | `worldcup_2026` | |

`PORT` is provided automatically by most platforms; the container's `start_hf.py` reads it.

### What happens on boot
`start_hf.py` runs `seed.py` (idempotent upsert of the 72 real group-stage fixtures) and then launches `uvicorn server:app`. The agent + read-only MCP bridge initialize in the app's lifespan.

### Verify
```bash
curl https://<your-service>.com/api/health
# {"status":"ok","agent":"ready","database":"connected","provider":"google_generativeai",
#  "model":"gemini-3-flash-preview","llm":"connected","mcp":"enabled (16 tools)", ...}
```
- `mcp: "enabled (N tools)"` → MCP bridge is up (Node present).
- **Copy this service URL** — the frontend needs it.

---

## 2. Frontend Deployment

1. Deploy the `frontend/` directory as a static site (Netlify, Vercel, etc).
2. Build command: `npm install && npm run build`
3. Publish directory: `dist`
4. SPA routing: configure rewrites so every path serves `/index.html`.

### Environment variables
| Key | Value | Why |
|-----|-------|-----|
| `VITE_API_URL` | `https://<your-backend>.com` | the frontend calls this for `/api/*` |

These are **build-time** variables (Vite inlines them), so set them **before** the first deploy.

---

## Local development

```bash
# backend (default port 8000)
cd backend && python -m uvicorn server:app --host 127.0.0.1 --port 8000
# frontend (port 5173) — create frontend/.env.local with VITE_API_URL=http://localhost:8000
cd frontend && npm run dev
```
Root `.env` holds `GOOGLE_API_KEY`, `MONGODB_URI`, `DATABASE_NAME` for the backend. Seed real fixtures with `cd backend && python seed.py` (idempotent).

---

## Troubleshooting

| Symptom | Cause / Fix |
|---|---|
| Frontend loads but body is blank | `VITE_BASE` not set correctly |
| Chat hits the wrong backend / CORS errors | `VITE_API_URL` missing or wrong |
| `/api/health` shows `mcp: "disabled"` | Runtime has no Node → install Node.js or use Docker |
| `/api/health` shows `database: "disconnected"` | Atlas IP allowlist missing or wrong `MONGODB_URI` |
| Plans empty / agent error | Bad/at-quota `GOOGLE_API_KEY` — the code retries on 429 automatically |
