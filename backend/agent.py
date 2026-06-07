"""In-process AI agent: Gemini (via OpenRouter) function-calling loop + MongoDB MCP bridge.

This used to be a standalone FastAPI microservice (`agent_server.py`). It now runs in the
same process as the backend gateway — `server.py` calls `process_message()` directly instead
of proxying over HTTP.
"""
from __future__ import annotations

import json
import logging
from typing import Any

from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL
from tools import TOOL_DEFINITIONS as CUSTOM_TOOL_DEFS
from tools import TOOL_REGISTRY as CUSTOM_TOOL_REGISTRY

logger = logging.getLogger("agent")

SYSTEM_PROMPT = (
    "You are an AI travel agent for the 2026 FIFA World Cup across USA, Canada, and Mexico. "
    "Your job is to plan the perfect trip for fans.\n\n"
    "TOOLS:\n"
    "1. Domain tools (search_matches, save_plan, get_plan, update_plan) — use these for trip planning.\n"
    "2. MongoDB MCP tools (prefixed with mcp_) — use these for raw database queries when you need "
    "to inspect or manipulate data directly.\n\n"
    "WORKFLOW when a user asks you to plan, build, or save a trip:\n"
    "1. ALWAYS call search_matches FIRST to get real fixtures. Never invent matches, dates, or venues.\n"
    "2. Build a COMPLETE plan and then call save_plan(). Always call save_plan when the user wants a trip — "
    "do not just describe the plan in text.\n\n"
    "The plan_data you pass to save_plan MUST be complete and use this exact structure:\n"
    "- matches: an array containing EVERY match the supporter's team plays within their dates. Pass each "
    "match object through EXACTLY as search_matches returned it (keep home_team, away_team, date, time, "
    "venue, city, country, match_id) — do not collapse it into a single string.\n"
    "- hotels: an array of hotel objects {name, location, stars, price_per_night, amenities[]}.\n"
    "- days: a day-by-day array {title, date, match, hotel, activities:[{title, desc, time, icon}]} covering the trip.\n"
    "- budget: the total trip budget as a number, and categories: an array of {label, amount} that sums to it.\n"
    "- travelers: the number of travelers.\n\n"
    "Keep the budget realistic for the number of travelers. Be enthusiastic — this is the World Cup!"
)

MAX_TOOL_TURNS = 6

client: Any = None
COMBINED_TOOL_DEFS: list[dict] = list(CUSTOM_TOOL_DEFS)
MCP_TOOL_NAMES: set[str] = set()


async def init_agent() -> None:
    """Initialise the OpenRouter client and (optionally) the MongoDB MCP bridge."""
    global client, COMBINED_TOOL_DEFS, MCP_TOOL_NAMES

    if not OPENROUTER_API_KEY:
        logger.error("OPENROUTER_API_KEY is not set. Agent will not function until it is configured.")
    else:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL,
            default_headers={
                "HTTP-Referer": "http://localhost:5173",
                "X-Title": "Fanfare",
            },
        )
        logger.info("OpenRouter client initialized (model=%s)", OPENROUTER_MODEL)

    from mcp_bridge import get_mcp_function_definitions, init_mcp

    mcp_ok = await init_mcp()
    if mcp_ok:
        mcp_defs = get_mcp_function_definitions()
        MCP_TOOL_NAMES = {d["name"] for d in mcp_defs}
        COMBINED_TOOL_DEFS = list(CUSTOM_TOOL_DEFS) + mcp_defs
        logger.info("MCP tools registered: %d custom + %d mcp = %d total",
                    len(CUSTOM_TOOL_DEFS), len(mcp_defs), len(COMBINED_TOOL_DEFS))
    else:
        logger.info("Running with %d custom tools only", len(CUSTOM_TOOL_DEFS))


async def close_agent() -> None:
    from mcp_bridge import close_mcp
    await close_mcp()


def agent_status() -> dict:
    return {
        "provider": "openrouter",
        "model": OPENROUTER_MODEL,
        "llm": "connected" if client else "not configured",
        "mcp": f"enabled ({len(MCP_TOOL_NAMES)} tools)" if MCP_TOOL_NAMES else "disabled",
        "custom_tools": len(CUSTOM_TOOL_DEFS),
        "total_tools": len(COMBINED_TOOL_DEFS),
    }


def _resolve_refs(obj: Any, defs: dict[str, Any] | None = None) -> Any:
    if isinstance(obj, dict):
        resolved_defs = obj.get("$defs") if defs is None else defs
        if "$ref" in obj and resolved_defs:
            ref = obj["$ref"]
            if ref.startswith("#/$defs/"):
                key = ref[len("#/$defs/"):]
                if key in resolved_defs:
                    return _resolve_refs(resolved_defs[key], resolved_defs)
        return {k: _resolve_refs(v, resolved_defs) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_resolve_refs(item, defs) for item in obj]
    return obj


def _sanitize_schema(obj):
    obj = _resolve_refs(obj)
    FORBIDDEN_KEYS = {
        'additionalproperties', 'additional_properties',
        'anyof', 'oneof', 'allof', 'not',
        'if', 'then', 'else', 'dependentschemas',
        'discriminator', 'xml', 'deprecated',
        '$schema', '$id', '$ref', '$defs', '$vocabulary',
        'definitions', '$comment',
    }
    if isinstance(obj, dict):
        result = {}
        for k, v in obj.items():
            if k.lower() in FORBIDDEN_KEYS:
                continue
            result[k] = _sanitize_schema(v)
        return result
    if isinstance(obj, list):
        return [_sanitize_schema(item) for item in obj]
    return obj


def _build_tools():
    if not client:
        return None

    tools = []
    for td in COMBINED_TOOL_DEFS:
        # Deep sanitize parameters to keep only provider-compatible JSON schema
        params = _sanitize_schema(dict(td["parameters"]))
        tools.append({
            "type": "function",
            "function": {
                "name": td["name"],
                "description": td["description"],
                "parameters": params,
            },
        })
    return tools


async def _execute_tool_async(name: str, args: dict) -> dict:
    if name in CUSTOM_TOOL_REGISTRY:
        logger.info("Executing custom tool: %s", name)
        result = CUSTOM_TOOL_REGISTRY[name](**args)
        return {"result": result}

    if name in MCP_TOOL_NAMES:
        logger.info("Executing MCP tool: %s", name)
        from mcp_bridge import call_mcp_tool
        return await call_mcp_tool(name, args)

    logger.error("Unknown tool called: %s", name)
    return {"result": {"error": f"Unknown tool: {name}"}}


async def process_message(
    message: str,
    history: list[dict],
) -> tuple[str, dict | None, list[dict] | None]:
    if not client:
        return "Agent is not configured. Please set OPENROUTER_API_KEY and restart.", None, None

    tools = _build_tools()

    messages: list[dict[str, Any]] = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history:
        role = "user" if msg.get("role") == "user" else "assistant"
        text = msg.get("text", msg.get("content", ""))
        if text:
            messages.append({"role": role, "content": text})

    messages.append({"role": "user", "content": message})

    tool_calls_log: list[dict] = []
    latest_plan_data: dict | None = None

    for turn in range(MAX_TOOL_TURNS):
        try:
            resp = await client.chat.completions.create(
                model=OPENROUTER_MODEL,
                messages=messages,
                tools=tools,
                temperature=0.5,
                max_tokens=2048,
            )
        except Exception as e:
            logger.error("OpenRouter API call failed: %s", e, exc_info=True)
            return f"I'm sorry, I encountered an error communicating with the AI service: {e}", latest_plan_data, (tool_calls_log if tool_calls_log else None)

        if not resp.choices:
            logger.warning("No choices returned by the model")
            return "I'm sorry, I couldn't process that request.", None, None

        msg = resp.choices[0].message
        tool_calls = msg.tool_calls or []

        if not tool_calls:
            reply = (msg.content or "").strip() or "Let me know how I can help with your World Cup trip!"
            return reply, latest_plan_data, (tool_calls_log if tool_calls_log else None)

        # Echo the assistant turn back, preserving Gemini 3 "thought signatures"
        # (reasoning_details) — required by Google for multi-turn function calling.
        assistant_msg: dict[str, Any] = {
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in tool_calls
            ],
        }
        reasoning_details = getattr(msg, "reasoning_details", None)
        if reasoning_details:
            assistant_msg["reasoning_details"] = reasoning_details
        messages.append(assistant_msg)

        for tc in tool_calls:
            fc_name = tc.function.name
            try:
                fc_args = json.loads(tc.function.arguments) if tc.function.arguments else {}
            except json.JSONDecodeError:
                logger.warning("Could not parse tool arguments: %s", tc.function.arguments)
                fc_args = {}
            logger.info("Turn %d — model called: %s(%s)", turn + 1, fc_name, fc_args)

            tool_result = await _execute_tool_async(fc_name, fc_args)

            tool_calls_log.append({
                "turn": turn + 1,
                "tool": fc_name,
                "args": fc_args,
                "result": tool_result,
            })

            if fc_name == "save_plan":
                plan_data_raw = tool_result.get("result", {})
                if isinstance(plan_data_raw, dict) and plan_data_raw.get("plan_id"):
                    latest_plan_data = plan_data_raw

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": json.dumps(tool_result, default=str),
            })

    return "Let me know if you'd like to refine the plan further!", latest_plan_data, tool_calls_log
