from __future__ import annotations

import asyncio
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from agent import agent_status, close_agent, init_agent, process_message
from db import (
    add_message,
    close,
    create_session,
    get_history,
    get_plan,
    get_session,
    update_plan as db_update_plan,
)
from models import (
    ChatRequest,
    ChatResponse,
    HistoryEntry,
    PlanResponse,
    PlanUpdateRequest,
    SessionResponse,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger("backend_server")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("World Cup 2026 app starting — initialising in-process agent")
    await init_agent()
    yield
    await close_agent()
    close()
    logger.info("App shut down")


app = FastAPI(title="World Cup 2026 Agent", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _history_for_agent(messages: list[dict]) -> list[dict]:
    result = []
    for msg in messages:
        role = msg.get("role", "user")
        text = msg.get("content", msg.get("reply", ""))
        if text:
            result.append({"role": role, "text": text})
    return result


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    loop = asyncio.get_running_loop()
    
    # Wrap synchronous database calls in executor to avoid blocking
    session_id = request.session_id or await loop.run_in_executor(None, create_session)
    if request.session_id:
        exists = await loop.run_in_executor(None, lambda: get_session(request.session_id))
        if not exists:
            session_id = await loop.run_in_executor(None, create_session)
    
    history = await loop.run_in_executor(None, lambda: _history_for_agent(get_history(session_id)))

    logger.info("Chat | session=%s | message_len=%d | history=%d turns",
                session_id, len(request.message), len(history))

    try:
        reply, plan_data, tool_calls = await process_message(request.message, history)
    except Exception as e:
        logger.error("Agent processing failed: %s", e, exc_info=True)
        raise HTTPException(status_code=502, detail="Agent processing error")

    # Save messages in background to avoid blocking the response
    await loop.run_in_executor(None, lambda: add_message(session_id, "user", request.message))
    await loop.run_in_executor(None, lambda: add_message(session_id, "assistant", reply, plan_data=plan_data))

    logger.info("Response | session=%s | reply_len=%d | plan=%s | tools=%d",
                session_id, len(reply), "yes" if plan_data else "no", len(tool_calls) if tool_calls else 0)

    return ChatResponse(
        reply=reply,
        plan_data=plan_data,
        session_id=session_id,
        tool_calls=tool_calls,
    )


@app.get("/api/plans/{plan_id}", response_model=PlanResponse)
async def get_plan_endpoint(plan_id: str):
    plan = get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return PlanResponse(
        plan_id=plan.get("plan_id", plan_id),
        plan_data=plan.get("plan_data"),
        user_id=plan.get("user_id"),
        created_at=plan.get("created_at"),
        updated_at=plan.get("updated_at"),
    )


@app.put("/api/plans/{plan_id}")
async def update_plan_endpoint(plan_id: str, body: PlanUpdateRequest):
    ok = db_update_plan(plan_id, body.updates)
    if not ok:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {"plan_id": plan_id, "message": "Plan updated"}


@app.get("/api/sessions/{session_id}", response_model=SessionResponse)
async def get_session_endpoint(session_id: str):
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    messages = session.get("messages", [])
    return SessionResponse(
        session_id=session_id,
        message_count=len(messages),
        created_at=session.get("created_at"),
        updated_at=session.get("updated_at"),
    )


@app.get("/api/history/{session_id}")
async def get_history_endpoint(session_id: str):
    messages = get_history(session_id)
    if not messages:
        raise HTTPException(status_code=404, detail="Session not found or empty")
    return [HistoryEntry(**m) for m in messages]


@app.get("/api/health")
async def health():
    status_info = agent_status()
    agent_ok = status_info["llm"] == "connected"

    db_ok = False
    try:
        from db import get_db as db_conn
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, lambda: db_conn().command("ping"))
        db_ok = True
    except Exception as e:
        logger.warning("Database health check failed: %s", e)

    status = "ok" if agent_ok and db_ok else "degraded" if agent_ok or db_ok else "down"
    return {
        "status": status,
        "agent": "ready" if agent_ok else "degraded",
        "database": "connected" if db_ok else "disconnected",
        **status_info,
    }


frontend_dist = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend", "dist")
if os.path.isdir(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
    logger.info("Frontend SPA mounted from %s", frontend_dist)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
