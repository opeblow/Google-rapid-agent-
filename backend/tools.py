from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from bson import ObjectId
from db import get_collection

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
            "description": "The complete trip plan. Fill in EVERY section below.",
            "properties": {
                "travelers": {"type": "integer", "description": "Number of travelers"},
                "budget": {"type": "number", "description": "Total trip budget in USD (a single number)"},
                "matches": {
                    "type": "array",
                    "description": "EVERY match the supporter's team plays that fits the trip. Pass each match object through EXACTLY as returned by search_matches — do not rename or drop fields.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "home_team": {"type": "string"},
                            "away_team": {"type": "string"},
                            "date": {"type": "string", "description": "YYYY-MM-DD"},
                            "time": {"type": "string", "description": "HH:MM"},
                            "venue": {"type": "string"},
                            "city": {"type": "string"},
                            "country": {"type": "string", "description": "USA, Canada, or Mexico"},
                            "stage": {"type": "string"},
                            "match_id": {"type": "string"},
                        },
                    },
                },
                "hotels": {
                    "type": "array",
                    "description": "One or more recommended hotels (an array, even if just one).",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "location": {"type": "string", "description": "City or neighbourhood"},
                            "stars": {"type": "integer"},
                            "price_per_night": {"type": "number", "description": "Nightly rate in USD"},
                            "amenities": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                },
                "days": {
                    "type": "array",
                    "description": "Day-by-day schedule covering the trip.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "e.g. 'Day 1 — Arrival in Atlanta'"},
                            "date": {"type": "string", "description": "YYYY-MM-DD"},
                            "match": {"type": "string", "description": "Match that day, e.g. 'Brazil vs Croatia', if any"},
                            "hotel": {"type": "string", "description": "Where they stay that night"},
                            "activities": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "title": {"type": "string"},
                                        "desc": {"type": "string"},
                                        "time": {"type": "string"},
                                        "icon": {"type": "string", "description": "A single emoji"},
                                    },
                                },
                            },
                        },
                    },
                },
                "categories": {
                    "type": "array",
                    "description": "Budget broken down by category; amounts should sum to roughly the total budget.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "label": {"type": "string", "description": "e.g. Flights, Hotels, Tickets, Food, Transport, Activities"},
                            "amount": {"type": "number", "description": "USD allocated to this category"},
                        },
                    },
                },
            },
        },
    },
    "description": "Save a complete trip plan for a user. Build the FULL plan_data (matches, hotels, days, budget categories) before calling. Returns a unique plan ID.",
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


def _normalize_match(m: dict, matches_col) -> dict:
    """Coerce a model-produced match into the shape MatchTimeline expects, and
    re-hydrate the canonical fields from the DB so cards always show real data."""
    if not isinstance(m, dict):
        return {}
    m = dict(m)
    # Split a paraphrased "Home vs Away" string into teams.
    if not m.get("home_team"):
        label = m.get("match") or m.get("teams") or m.get("title") or ""
        parts = re.split(r"\s+(?:vs\.?|v|—|-)\s+", str(label), maxsplit=1)
        if len(parts) == 2:
            m["home_team"], m["away_team"] = parts[0].strip(), parts[1].strip()

    # Re-hydrate from the matches collection (by id, else by teams + date).
    doc = None
    try:
        if m.get("match_id"):
            doc = matches_col.find_one({"match_id": m["match_id"]})
        if not doc and m.get("home_team") and m.get("away_team"):
            q = {
                "home_team": {"$regex": f"^{re.escape(m['home_team'])}$", "$options": "i"},
                "away_team": {"$regex": f"^{re.escape(m['away_team'])}$", "$options": "i"},
            }
            if m.get("date"):
                q["date"] = m["date"]
            doc = matches_col.find_one(q)
    except Exception:
        doc = None
    if doc:
        for k in ("home_team", "away_team", "date", "time", "venue", "city", "country", "stage", "match_id"):
            if doc.get(k) is not None:
                m[k] = doc[k]
    return m


def _normalize_hotel(h: dict) -> dict:
    if not isinstance(h, dict):
        return {}
    h = dict(h)
    if "price_per_night" not in h:
        for alt in ("cost_per_night", "price", "nightly_rate", "rate", "cost"):
            if alt in h:
                h["price_per_night"] = h.pop(alt)
                break
    if "stars" not in h and "rating" in h:
        h["stars"] = h.pop("rating")
    if "location" not in h:
        for alt in ("address", "city", "area", "neighbourhood", "neighborhood"):
            if h.get(alt):
                h["location"] = h[alt]
                break
    return h


def _normalize_plan(plan_data: dict) -> dict:
    """Map whatever shape the model emitted onto the canonical plan the UI renders.
    Best-effort and defensive — never raises."""
    if not isinstance(plan_data, dict):
        return plan_data
    try:
        pd = dict(plan_data)
        matches_col = get_collection("matches")

        # matches: array of canonical match objects
        raw_matches = pd.get("matches")
        if isinstance(raw_matches, list):
            pd["matches"] = [_normalize_match(m, matches_col) for m in raw_matches]

        # hotels: ensure an array; fold a singular "hotel" object in
        hotels = pd.get("hotels")
        if not isinstance(hotels, list):
            hotels = [hotels] if isinstance(hotels, dict) else []
        if isinstance(pd.get("hotel"), dict):
            hotels = hotels + [pd.pop("hotel")]
        if hotels:
            pd["hotels"] = [_normalize_hotel(h) for h in hotels if isinstance(h, dict)]

        # days: accept common aliases
        if not isinstance(pd.get("days"), list):
            for alt in ("daily_plan", "itinerary", "schedule", "daily_schedule"):
                if isinstance(pd.get(alt), list):
                    pd["days"] = pd[alt]
                    break

        # budget categories: accept aliases, coerce {name/cost} -> {label/amount}
        cats = pd.get("categories")
        if not isinstance(cats, list):
            for alt in ("budget_breakdown", "breakdown", "budget_categories"):
                if isinstance(pd.get(alt), list):
                    cats = pd[alt]
                    break
        if isinstance(cats, list):
            norm = []
            for c in cats:
                if not isinstance(c, dict):
                    continue
                norm.append({
                    "label": c.get("label") or c.get("name") or c.get("category") or "Other",
                    "amount": c.get("amount") or c.get("cost") or c.get("value") or 0,
                })
            pd["categories"] = norm

        # budget: ensure a scalar number
        b = pd.get("budget")
        if isinstance(b, dict):
            pd["budget"] = b.get("total") or b.get("amount") or sum(
                (c.get("amount") or 0) for c in pd.get("categories", [])
            ) or None

        return pd
    except Exception as e:
        logger.warning("Plan normalization failed (%s) — storing as-is", e)
        return plan_data


def save_plan(user_id: str, plan_data: dict) -> dict:
    try:
        plans_col = get_collection("plans")
        plan_data = _normalize_plan(plan_data)
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
