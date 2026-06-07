---
title: Fanfare — AI World Cup 2026 Trip Planner
emoji: 🏆
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
---

# Fanfare — AI World Cup 2026 Trip Planner

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

An AI-powered travel planning agent for the 2026 FIFA World Cup, built across 16 host cities in the USA, Canada, and Mexico. Powered by Google Gemini, MongoDB MCP Server, and a three-tier microservice architecture.

Built for the **Google Cloud Rapid Agent Hackathon (MongoDB Track)**.

---

## Quick Start (Windows)

```powershell
# 1. Install Python dependencies
cd agent; pip install -r requirements.txt; cd ..\backend; pip install -r requirements.txt; cd ..\frontend; npm install; cd ..

# 2. Configure .env (copy from .env.example files or use root .env)
#    Must set: GEMINI_API_KEY, MONGODB_URI

# 3. Seed matches into MongoDB
cd agent; python seed.py; cd ..

# 4. Start Agent service (Terminal 1)
cd agent; python -c "import uvicorn; uvicorn.run('agent_server:app', host='0.0.0.0', port=8001)"
# Expected output:
#   INFO:     Started server process [XXXX]
#   INFO:     Gemini client initialized
#   INFO:     MCP bridge skipped (or timed out) — running with 4 custom tools
#   INFO:     Application startup complete.
#   INFO:     Uvicorn running on http://0.0.0.0:8001

# 5. Start Backend service (Terminal 2)
cd backend; python -c "import uvicorn; uvicorn.run('server:app', host='0.0.0.0', port=8000)"
# Expected output:
#   INFO:     Started server process [XXXX]
#   INFO:     Backend gateway starting — agent at http://localhost:8001
#   INFO:     Application startup complete.
#   INFO:     Uvicorn running on http://0.0.0.0:8000

# 6. Start Frontend (Terminal 3)
cd frontend; npm run dev
# Expected output:
#   VITE v5.x.x  ready in XXX ms
#   Local:   http://localhost:5173/

# 7. Verify health
curl http://localhost:8000/api/health
# Expected: {"status":"ok","agent":"reachable","database":"connected"}

curl http://localhost:8001/agent/health
# Expected: {"status":"ok","gemini":"connected","mcp":"disabled","custom_tools":4,"total_tools":4}

# 8. Test chat (replace KEY if your API key has quota)
curl -X POST http://localhost:8000/api/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"message\": \"Find matches in New York\"}"
# Expected: {"reply":"...match results...","session_id":"...","tool_calls":[...]}
```

---

## Architecture

```
                          Frontend (React + Vite)
                               |
                          Backend API (FastAPI :8000)
                          /                    \
                    Agent Service         MongoDB (Atlas)
                  (FastAPI :8001)         (Matches, Plans,
                  Gemini + MCP               Sessions)
```

The system is split into three independent, deployable services:

| Service | Directory | Port | Purpose |
|---------|-----------|------|---------|
| Agent | `agent/` | 8001 | Gemini-powered AI agent with custom tools + MongoDB MCP Server integration |
| Backend | `backend/` | 8000 | API gateway managing sessions, plans, and proxying chat to the agent |
| Frontend | `frontend/` | 5173 | React SPA with onboarding wizard, live chat, and itinerary dashboard |

---

## Features

**Agent Service**
- Multi-turn Gemini function calling with tool execution (up to 6 turns per request)
- Domain-specific tools: `search_matches`, `save_plan`, `get_plan`, `update_plan`
- MongoDB MCP Server bridge exposing full database CRUD as callable tools (`mcp_find`, `mcp_insert_one`, `mcp_aggregate`, etc.)
- 48 pre-seeded World Cup 2026 matches across all 16 host cities
- Conversation history management and plan data extraction

**Backend Gateway**
- Session-based conversation history persisted in MongoDB
- Proxies chat messages to the agent service with timeout handling
- RESTful endpoints for plans and session history
- Health check endpoint monitoring both the agent and database

**Frontend Application**
- Full-screen landing page with hero section and feature highlights
- 3-step onboarding wizard: team selection, trip details, preferences
- Split-panel dashboard: live chat on the left, interactive itinerary on the right
- Itinerary tabs: Match Timeline, Daily Plan (accordion), Budget Breakdown (CSS bars), Hotel Cards
- Saved Plans page with localStorage persistence
- Dark mode with system preference detection
- Responsive design with mobile tab switching

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| AI Engine | Google Gemini (`gemini-2.0-flash`) via `google-genai` SDK |
| Partner Integration | MongoDB MCP Server (Model Context Protocol) |
| Backend API | FastAPI, Uvicorn, Pydantic |
| Database | MongoDB (Atlas or local) via PyMongo |
| Frontend | React 18, Vite, Tailwind CSS, react-router-dom |
| HTTP Client | Axios (frontend), httpx (backend) |
| Markdown | react-markdown for AI response rendering |
| Icons | @heroicons/react |

---

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 20+ (for MongoDB MCP Server integration)
- MongoDB Atlas cluster (or local MongoDB instance)
- Google Gemini API key

### 1. Clone and install dependencies

```bash
# Agent service
cd agent
pip install -r requirements.txt

# Backend service
cd ../backend
pip install -r requirements.txt

# Frontend app
cd ../frontend
npm install
```

### 2. Configure environment variables

Create a `.env` file in the project **root** directory (both services read from it):

```
GEMINI_API_KEY=your_gemini_api_key_here
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/worldcup_2026
DATABASE_NAME=worldcup_2026
AGENT_SERVICE_URL=http://localhost:8001
```

Each service also has its own `.env.example` for reference.

> **MCP integration**: The MongoDB MCP Server activates automatically when you use an Atlas connection string (`mongodb+srv://...`). If you use `mongodb://localhost:27017`, the agent runs with custom tools only and skips the MCP bridge. The first `npx` download may take ~30s — the bridge has a built-in 30s timeout; it falls back gracefully to custom tools only.

### 3. Seed match data

```bash
cd agent
python seed.py
```

Expected output:
```
INFO | db | Connected to MongoDB at mongodb+srv://...
INFO | __main__ | Seeded 48 World Cup 2026 matches across 16 host cities
INFO | __main__ | Seeding complete.
```

This populates the `matches` collection with 48 World Cup matches across all 16 host cities. If the collection already contains data, the seeder skips insertion.

### 4. Start services

Run each in a separate terminal:

```bash
# Terminal 1 -- Agent (port 8001)
cd agent
python -c "import uvicorn; uvicorn.run('agent_server:app', host='0.0.0.0', port=8001)"
```

Expected output:
```
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
INFO:     Gemini client initialized
INFO:     MCP bridge initialization timed out after 30s   (or "MCP bridge ready — N tools")
INFO:     Running with 4 custom tools only
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001
```

```bash
# Terminal 2 -- Backend (port 8000)
cd backend
python -c "import uvicorn; uvicorn.run('server:app', host='0.0.0.0', port=8000)"
```

Expected output:
```
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
INFO:     Backend gateway starting — agent at http://localhost:8001
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

```bash
# Terminal 3 -- Frontend (port 5173)
cd frontend
npm run dev
```

Expected output:
```
VITE v5.x.x  ready in XXX ms
  Local:   http://localhost:5173/
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

### 5. Verify

```bash
# Health check — both should return 200
curl http://localhost:8000/api/health
# → {"status":"ok","agent":"reachable","database":"connected"}

curl http://localhost:8001/agent/health
# → {"status":"ok","gemini":"connected","mcp":"disabled","custom_tools":4,"total_tools":4}
```

### 6. Test a chat

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Find matches in New York on June 15"}'
```

Expected response format:
```json
{
  "reply": "Here are matches in New York/New Jersey...",
  "session_id": "abc123def456",
  "plan_data": null,
  "tool_calls": [
    {"turn": 1, "tool": "search_matches", "args": {"city": "New York/New Jersey", "date": "2026-06-15"}, "result": {...}}
  ]
}
```

If your Gemini API key has hit the free quota, the reply will be:
```
"I'm sorry, I encountered an error communicating with the AI service: 429 RESOURCE_EXHAUSTED..."
```
Generate a new key at https://aistudio.google.com/apikey and update `.env`.

---

## API Reference

### Backend Gateway (`:8000`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | Send a message to the agent (creates or continues a session) |
| GET | `/api/plans/{plan_id}` | Retrieve a saved trip plan |
| PUT | `/api/plans/{plan_id}` | Update fields on a saved plan |
| GET | `/api/sessions/{session_id}` | Get session metadata |
| GET | `/api/history/{session_id}` | Get full message history for a session |
| GET | `/api/health` | Health check (agent + database status) |

### Agent Service (`:8001`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/agent/process` | Process a message with Gemini + tools |
| GET | `/agent/health` | Health check (Gemini + MCP status) |

---

## Project Structure

```
.
├── agent/                      # AI Agent microservice
│   ├── agent_server.py         # FastAPI server with Gemini function calling loop
│   ├── tools.py                # Custom domain tools (search_matches, save_plan, etc.)
│   ├── mcp_bridge.py           # MongoDB MCP Server client bridge
│   ├── db.py                   # MongoDB connection (matches, plans collections)
│   ├── seed.py                 # 48-match seeder
│   ├── config.py               # Environment configuration
│   └── requirements.txt
├── backend/                    # Backend API gateway
│   ├── server.py               # FastAPI server with session management
│   ├── db.py                   # MongoDB connection (sessions, plans collections)
│   ├── models.py               # Pydantic request/response models
│   ├── config.py               # Environment configuration
│   └── requirements.txt
├── frontend/                   # React application
│   ├── src/
│   │   ├── pages/              # Landing, Onboarding, Dashboard, SavedPlans
│   │   ├── components/         # 24 reusable UI components
│   │   ├── App.jsx             # Router and layout
│   │   ├── api.js              # Axios client
│   │   └── index.css           # Tailwind directives + custom styles
│   ├── public/favicon.svg
│   ├── index.html
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── package.json
└── LICENSE                     # Apache 2.0
```

---

## Partner Integration: MongoDB MCP Server

This project integrates the **MongoDB MCP Server** as required for the MongoDB track prize bucket. The MCP bridge (`agent/mcp_bridge.py`):

1. Spawns the MongoDB MCP Server as a subprocess via `npx mongodb-mcp-server`
2. Discovers available MCP tools (find, insert, update, aggregate, etc.)
3. Converts MCP tool definitions to Gemini-compatible `FunctionDeclaration` objects
4. Routes function calls from Gemini through the MCP protocol to MongoDB
5. Returns structured results back to the model

All MCP tools are prefixed with `mcp_` and available alongside the agent's custom domain tools. The system prompt instructs Gemini which tools to use for which task.

---

## License

Copyright 2026. All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
