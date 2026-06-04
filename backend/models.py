from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    plan_data: dict | None = None
    session_id: str
    tool_calls: list[dict] | None = None


class PlanResponse(BaseModel):
    plan_id: str
    plan_data: dict | None = None
    user_id: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class PlanUpdateRequest(BaseModel):
    updates: dict


class SessionResponse(BaseModel):
    session_id: str
    message_count: int
    created_at: str | None = None
    updated_at: str | None = None


class HistoryEntry(BaseModel):
    role: str
    content: str
    timestamp: str | None = None
    plan_data: dict | None = None


class HealthResponse(BaseModel):
    status: str
    agent: str
    database: str
