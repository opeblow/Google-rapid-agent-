from __future__ import annotations

import logging
from datetime import datetime, timezone
from bson import ObjectId
from .db import get_collection

logger = logging.getLogger(__name__)

SEARCH_MATCHES_SCHEMA = {
    "type": "object",
    "properties": {
        "team": {
            "type": "string",
            "description": "Team name (e.g. 'Brazil', 'USA')",
        },
        "host_city": {
            "type": "string",
            "description": "Host city (e.g. 'New York/New Jersey', 'Mexico City')",
        },
        "date": {
            "type": "string",
            "description": "Match date in YYYY-MM-DD format (e.g. '2026-06-12')",
        },
    },
    "description": "Search for World Cup 2026 matches by team, host city, or date. All parameters are optional.",
}

SAVE_PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "user_id": {
            "type": "string",
            "description": "Unique identifier for the user",
        },
        "plan_data": {
            "type": "object",
            "description": "The full trip plan object containing matches, hotels, transport, etc.",
            "properties": {
                "matches": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of matches the user plans to attend",
                },
                "hotel": {"type": "object", "description": "Hotel booking details"},
                "transport": {"type": "object", "description": "Transportation details"},
                "budget": {"type": "number", "description": "Estimated total budget"},
            },
        },
    },
    "description": "Save a complete trip plan for a user. Returns a unique plan ID.",
}

GET_PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "plan_id": {
            "type": "string",
            "description": "The unique ID of the plan to retrieve",
        },
    },
    "description": "Retrieve a saved trip plan by its ID.",
}

UPDATE_PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "plan_id": {
            "type": "string",
            "description": "The unique ID of the plan to update",
        },
        "updates": {
            "type": "object",
            "description": "Fields to update on the plan",
        },
    },
    "description": "Update an existing trip plan with new data.",
}

TOOL_DEFINITIONS = [
    {
        "name": "search_matches",
        "description": "Search for World Cup 2026 matches by team, host city, or date. Returns matching matches with venue, time, and ticket info.",
        "parameters": SEARCH_MATCHES_SCHEMA,
    },
    {
        "name": "save_plan",
        "description": "Save a complete trip plan for a user after building or updating their itinerary.",
        "parameters": SAVE_PLAN_SCHEMA,
    },
    {
        "name": "get_plan",
        "description": "Retrieve a previously saved trip plan by its plan ID.",
        "parameters": GET_PLAN_SCHEMA,
    },
    {
        "name": "update_plan",
        "description": "Update specific fields in an existing trip plan.",
        "parameters": UPDATE_PLAN_SCHEMA,
    },
]


def search_matches(team: str | None = None, host_city: str | None = None, date: str | None = None) -> list[dict]:
    try:
        matches_col = get_collection("matches")
        filters = {}
        if team:
            filters["$or"] = [
                {"home_team": {"$regex": team, "$options": "i"}},
                {"away_team": {"$regex": team, "$options": "i"}},
            ]
        if host_city:
            filters["city"] = {"$regex": host_city, "$options": "i"}
        if date:
            filters["date"] = date

        cursor = matches_col.find(filters).sort("date", 1).limit(20)
        results = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(doc)

        logger.info("search_matches(%s, %s, %s) → %d results", team, host_city, date, len(results))
        return results if results else [{"message": "No matches found matching your criteria."}]
    except Exception as e:
        logger.error("search_matches failed: %s", e, exc_info=True)
        return [{"error": f"Failed to search matches: {e}"}]


def save_plan(user_id: str, plan_data: dict) -> dict:
    try:
        plans_col = get_collection("plans")
        doc = {
            "user_id": user_id,
            "plan_data": plan_data,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        result = plans_col.insert_one(doc)
        plan_id = str(result.inserted_id)
        logger.info("save_plan(user_id=%s) → plan_id=%s", user_id, plan_id)
        return {
            "plan_id": plan_id,
            "message": "Plan saved successfully!",
            "plan_data": plan_data,
        }
    except Exception as e:
        logger.error("save_plan failed: %s", e, exc_info=True)
        return {"error": f"Failed to save plan: {e}"}


def get_plan(plan_id: str) -> dict:
    try:
        plans_col = get_collection("plans")
        doc = plans_col.find_one({"_id": ObjectId(plan_id)})
        if not doc:
            logger.warning("get_plan(%s) → not found", plan_id)
            return {"error": "Plan not found. Please check the plan ID and try again."}
        doc["_id"] = str(doc["_id"])
        logger.info("get_plan(%s) → found", plan_id)
        return doc
    except Exception as e:
        logger.error("get_plan failed: %s", e, exc_info=True)
        return {"error": f"Failed to retrieve plan: {e}"}


def update_plan(plan_id: str, updates: dict) -> dict:
    try:
        plans_col = get_collection("plans")
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        result = plans_col.update_one(
            {"_id": ObjectId(plan_id)},
            {"$set": updates},
        )
        if result.matched_count == 0:
            logger.warning("update_plan(%s) → not found", plan_id)
            return {"error": "Plan not found. Please check the plan ID and try again."}
        logger.info("update_plan(%s) → updated", plan_id)
        return {"plan_id": plan_id, "message": "Plan updated successfully!", "updates": updates}
    except Exception as e:
        logger.error("update_plan failed: %s", e, exc_info=True)
        return {"error": f"Failed to update plan: {e}"}


TOOL_REGISTRY = {
    "search_matches": search_matches,
    "save_plan": save_plan,
    "get_plan": get_plan,
    "update_plan": update_plan,
}


def execute_tool(name: str, args: dict) -> dict:
    func = TOOL_REGISTRY.get(name)
    if not func:
        logger.error("Unknown tool called: %s", name)
        return {"error": f"Unknown tool: {name}"}
    logger.info("Executing tool: %s with args: %s", name, args)
    result = func(**args)
    return {"result": result}
