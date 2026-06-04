import logging
from datetime import datetime, timezone
from uuid import uuid4

from pymongo import MongoClient
from pymongo.collection import Collection
from config import MONGODB_URI, DATABASE_NAME

logger = logging.getLogger(__name__)

_client: MongoClient | None = None


def get_db():
    global _client
    if _client is None:
        _client = MongoClient(MONGODB_URI)
        logger.info("Backend connected to MongoDB at %s", MONGODB_URI)
    return _client[DATABASE_NAME]


def get_collection(name: str) -> Collection:
    return get_db()[name]


def close():
    global _client
    if _client:
        _client.close()
        _client = None
        logger.info("Backend MongoDB connection closed")


def create_session() -> str:
    sessions = get_collection("sessions")
    session_id = uuid4().hex[:12]
    now = datetime.now(timezone.utc).isoformat()
    sessions.insert_one({
        "session_id": session_id,
        "messages": [],
        "created_at": now,
        "updated_at": now,
    })
    logger.info("Created session: %s", session_id)
    return session_id


def get_session(session_id: str) -> dict | None:
    sessions = get_collection("sessions")
    doc = sessions.find_one({"session_id": session_id}, {"_id": 0})
    return doc


def get_history(session_id: str) -> list[dict]:
    sessions = get_collection("sessions")
    doc = sessions.find_one({"session_id": session_id}, {"_id": 0, "messages": 1})
    return doc.get("messages", []) if doc else []


def add_message(session_id: str, role: str, content: str, plan_data: dict | None = None):
    sessions = get_collection("sessions")
    entry = {"role": role, "content": content, "timestamp": datetime.now(timezone.utc).isoformat()}
    if plan_data:
        entry["plan_data"] = plan_data
    now = datetime.now(timezone.utc).isoformat()
    result = sessions.update_one(
        {"session_id": session_id},
        {
            "$push": {"messages": entry},
            "$set": {"updated_at": now},
            "$setOnInsert": {"created_at": now},
        },
    )
    if result.matched_count == 0:
        sessions.update_one(
            {"session_id": session_id},
            {"$set": {"messages": [entry], "created_at": now, "updated_at": now}},
            upsert=True,
        )


def get_plan(plan_id: str) -> dict | None:
    plans = get_collection("plans")
    from bson import ObjectId
    try:
        doc = plans.find_one({"_id": ObjectId(plan_id)})
        if doc:
            doc["_id"] = str(doc["_id"])
            doc["plan_id"] = doc["_id"]
        return doc
    except Exception:
        return None


def update_plan(plan_id: str, updates: dict) -> bool:
    plans = get_collection("plans")
    from bson import ObjectId
    try:
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        result = plans.update_one(
            {"_id": ObjectId(plan_id)},
            {"$set": updates},
        )
        return result.matched_count > 0
    except Exception:
        return False
