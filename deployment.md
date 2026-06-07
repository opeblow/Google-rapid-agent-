# Deployment Guide

How to deploy WC2026 Agent: the **backend** (unified FastAPI app) on a cloud host and the **frontend** (React/Vite SPA), talking to **MongoDB Atlas**.

```
  Frontend (React SPA)  ──HTTPS──>  Backend (FastAPI + in-process agent)  ──>  MongoDB Atlas
                                     └─ Vertex AI (Gemini via google-cloud-aiplatform SDK)
                                     └─ MongoDB MCP Server (read-only, via npx)
```

Since the merge, the agent runs **in-process inside the backend** — there is only one service to deploy, not two.

---

## Prerequisites

- **MongoDB Atlas** cluster + connection string (`mongodb+srv://…`).
  - Atlas → **Network Access** → allow `0.0.0.0/0` (cloud hosts have dynamic IPs).
- **Google Cloud project** with Vertex AI API enabled.
  - A **service account** with `roles/aiplatform.user` IAM role.
  - For local dev, download the service account key and set `GOOGLE_APPLICATION_CREDENTIALS`.
  - For Cloud Run, attach the service account to the Cloud Run service.
- GitHub repo connected to your deploy platform.

---

## Deploy on Google Cloud Run

Deploy the backend container on Cloud Run for a fully managed Google Cloud experience:

```bash
# 1. Build and push to Artifact Registry
gcloud builds submit --config cloudbuild.yaml

# 2. Deploy to Cloud Run
gcloud run deploy wc2026-agent \
  --image us-central1-docker.pkg.dev/$PROJECT_ID/wc2026-agent/backend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 2 \
  --timeout 300 \
  --service-account "wc2026-agent-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --set-env-vars "LLM_PROVIDER=vertex_ai,VERTEX_AI_PROJECT=$PROJECT_ID,VERTEX_AI_LOCATION=us-central1,GEMINI_MODEL=gemini-3-flash-preview,DATABASE_NAME=worldcup_2026" \
  --set-secrets "MONGODB_URI=mongodb-uri:latest"
```

The service runs on **Vertex AI** (Google Cloud AI platform) — fully compliant with the hackathon's requirement for Google Cloud AI tools.

---

## 1. Backend Deployment

The agent's MongoDB MCP integration shells out to `npx mongodb-mcp-server`, so the runtime needs **Node.js**. The repo's root `Dockerfile` already installs both Python and Node.

### Environment variables
| Key | Value | Notes |
|-----|-------|-------|
| `LLM_PROVIDER` | `vertex_ai` | `vertex_ai` (default) or `ai_studio` |
| `VERTEX_AI_PROJECT` | `my-gcp-project` | Google Cloud project ID |
| `VERTEX_AI_LOCATION` | `us-central1` | GCP region |
| `GEMINI_MODEL` | `gemini-3-flash-preview` | optional (this is the default) |
| `MONGODB_URI` | `mongodb+srv://…` | required (secret) |
| `DATABASE_NAME` | `worldcup_2026` | |
| *(AI Studio fallback)* | | |
| `GOOGLE_API_KEY` | `AIza...` | only needed when `LLM_PROVIDER=ai_studio` |

`PORT` is provided automatically by most platforms; the container's `start_hf.py` reads it.

### What happens on boot
`start_hf.py` runs `seed.py` (idempotent upsert of the 72 real group-stage fixtures) and then launches `uvicorn server:app`. The agent + read-only MCP bridge initialize in the app's lifespan.

### Verify
```bash
curl https://<your-service>.com/api/health
# {"status":"ok","agent":"ready","database":"connected","provider":"vertex_ai",
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
Root `.env` holds Vertex AI settings (`VERTEX_AI_PROJECT`, `VERTEX_AI_LOCATION`), `MONGODB_URI`, `DATABASE_NAME` for the backend. For local dev without a GCP service account, set `LLM_PROVIDER=ai_studio` and `GOOGLE_API_KEY`. Seed real fixtures with `cd backend && python seed.py` (idempotent).

---

## Troubleshooting

| Symptom | Cause / Fix |
|---|---|
| Frontend loads but body is blank | `VITE_BASE` not set correctly |
| Chat hits the wrong backend / CORS errors | `VITE_API_URL` missing or wrong |
| `/api/health` shows `mcp: "disabled"` | Runtime has no Node → install Node.js or use Docker |
| `/api/health` shows `database: "disconnected"` | Atlas IP allowlist missing or wrong `MONGODB_URI` |
| `/api/health` shows `llm: "not configured"` | `VERTEX_AI_PROJECT` not set or ADC not configured — verify service account or set `LLM_PROVIDER=ai_studio` with `GOOGLE_API_KEY` |
| Plans empty / agent error | Vertex AI quota exhausted or auth issue — the code retries on 429 automatically |
