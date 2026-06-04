from __future__ import annotations

import logging
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from config import AGENT_SERVICE_URL
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
    HealthResponse,
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

AGENT_TIMEOUT = 60.0


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Backend gateway starting — agent at %s", AGENT_SERVICE_URL)
    yield
    close()
    logger.info("Backend gateway shut down")


app = FastAPI(title="World Cup 2026 Backend Gateway", version="1.0.0", lifespan=lifespan)


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

    session_id = request.session_id or create_session()
    if request.session_id and not get_session(session_id):
        session_id = create_session()
    history = _history_for_agent(get_history(session_id))

    logger.info("Chat | session=%s | message_len=%d | history=%d turns",
                session_id, len(request.message), len(history))

    try:
        async with httpx.AsyncClient(timeout=AGENT_TIMEOUT) as client:
            resp = await client.post(
                f"{AGENT_SERVICE_URL}/agent/process",
                json={"message": request.message, "history": history},
            )
            resp.raise_for_status()
            agent_data = resp.json()
    except httpx.ConnectError:
        logger.error("Agent service unreachable at %s", AGENT_SERVICE_URL)
        raise HTTPException(status_code=503, detail="Agent service is unavailable")
    except httpx.TimeoutException:
        logger.error("Agent service timed out after %ds", AGENT_TIMEOUT)
        raise HTTPException(status_code=504, detail="Agent service timed out")
    except httpx.HTTPStatusError as e:
        logger.error("Agent returned %s: %s", e.response.status_code, e.response.text)
        raise HTTPException(status_code=502, detail="Agent service error")

    reply = agent_data.get("reply", "")
    plan_data = agent_data.get("plan_data")
    tool_calls = agent_data.get("tool_calls")

    add_message(session_id, "user", request.message)
    add_message(session_id, "assistant", reply, plan_data=plan_data)

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


@app.get("/api/health", response_model=HealthResponse)
async def health():
    agent_ok = False
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{AGENT_SERVICE_URL}/agent/health")
            agent_ok = resp.status_code == 200
    except Exception:
        pass

    db_ok = False
    try:
        from db import get_db as db_conn
        db_conn().command("ping")
        db_ok = True
    except Exception:
        pass

    status = "ok" if agent_ok and db_ok else "degraded" if agent_ok or db_ok else "down"
    return HealthResponse(
        status=status,
        agent="reachable" if agent_ok else "unreachable",
        database="connected" if db_ok else "disconnected",
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
