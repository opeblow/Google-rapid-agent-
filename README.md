# WC2026 Agent — AI World Cup 2026 Trip Planner

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

An AI-powered travel planning agent for the **2026 FIFA World Cup**, built across **16 host cities** in the USA, Canada, and Mexico. Powered by **Google Vertex AI (Gemini 3 Flash)**, **MongoDB MCP Server**, and deployed on **Google Cloud Run**.

---

**Built for the [Google Cloud Rapid Agent Hackathon](https://rapid-agent.devpost.com/) — MongoDB Track.**

---

## Hackathon Requirements Met

| Requirement | Implementation |
|-------------|----------------|
| **Powered by Gemini** | Uses **Vertex AI** SDK (`google-cloud-aiplatform`) with `gemini-3-flash-preview` for multi-turn function calling |
| **Google Cloud AI Tools** | Built on **Vertex AI** (Google Cloud AI platform) — uses `vertexai.preview.generative_models` for Gemini access |
| **Partner MCP Integration** | Full **MongoDB MCP Server** integration — agent queries match data, plans, and sessions via read-only MCP tools |
| **Move Beyond Chat** | Agent executes real tools: `search_matches`, `save_plan`, `get_plan`, `update_plan` — not just text responses |
| **Multi-Step Missions** | Up to **6 tool turns** per request — agent plans steps, calls tools, processes results, and refines |
| **Real-World Challenge** | Solves the 2026 World Cup fan logistics problem: 48 teams, 16 cities, 3 countries, 104+ matches |
| **Open Source** | Apache 2.0 licensed — public repository with detectable license file |
| **Deployed on Google Cloud** | Containerized and deployable via **Cloud Run** (see `cloudbuild.yaml` and `deployment.md`) |

---

## Quick Start

```bash
# 1. Install dependencies
cd backend && pip install -r requirements.txt
cd ../frontend && npm install

# 2. Configure .env (copy from backend/.env.example)
#    For Vertex AI: set VERTEX_AI_PROJECT (uses ADC / service account)
#    For local dev: set LLM_PROVIDER=ai_studio and GOOGLE_API_KEY

# 3. Seed match data
cd backend && python seed.py

# 4. Start backend (port 8000)
cd backend && python -m uvicorn server:app --host 0.0.0.0 --port 8000

# 5. Start frontend (port 5173) in a separate terminal
cd frontend && npm run dev

# 6. Verify
curl http://localhost:8000/api/health
```

---

## Architecture

```
                         Frontend (React + Vite)
                              |
                    Backend API (FastAPI :8000)
                    /                        \
         Vertex AI (Gemini)              MongoDB (Atlas)
         Function-calling agent          (Matches, Plans,
         + MongoDB MCP Bridge             Sessions)
         (in-process)
```

| Layer | Technology |
|-------|-----------|
| AI Engine | **Vertex AI** — Gemini 3 Flash (`gemini-3-flash-preview`) via `google-cloud-aiplatform` |
| Partner Integration | MongoDB MCP Server (25+ read-only tools via Model Context Protocol) |
| Backend | FastAPI, Uvicorn, Pydantic |
| Database | MongoDB Atlas via PyMongo + MCP |
| Frontend | React 18, Vite, Tailwind CSS, Framer Motion |
| Deployment | Google Cloud Run (Docker + Artifact Registry) |

---

## How It Works

1. **User inputs** their supported team, budget, travel dates, and preferences via the onboarding wizard
2. **Gemini on Vertex AI** plans the trip — calls `search_matches` to find real fixtures, builds an itinerary with hotels, daily activities, and budget breakdown
3. **MongoDB MCP** provides read-only access to the match database (48 real group-stage fixtures across all 16 host cities)
4. **Agent saves the plan** via `save_plan` tool — persisted in MongoDB and rendered in the interactive dashboard
5. **User refines** through natural language chat — agent can update plans, search alternative matches, or adjust itineraries

---

## Submission Requirements

- **Hosted Project**: Deployed on Render/GCP — contact for URL
- **Code Repository**: This repo — public with Apache 2.0 license
- **Demo Video**: See `demo/` or contact for link
- **Track**: MongoDB Partner Track

---

## Tech Stack

- **Google Gemini 3 Flash** — multi-turn function calling with tool execution
- **MongoDB MCP Server** — Model Context Protocol for secure read-only database access
- **FastAPI** — high-performance async API gateway
- **React 18 + Vite** — responsive SPA with dark mode
- **Tailwind CSS** — utility-first styling with custom design system
- **Framer Motion** — smooth page transitions and animations

---

## License

Apache 2.0 — see [LICENSE](LICENSE).
