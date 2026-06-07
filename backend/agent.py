"""In-process AI agent: Gemini (Vertex AI) function-calling loop + MongoDB MCP bridge.

The agent runs in the same process as the backend gateway — `server.py` calls `process_message()`
directly instead of proxying over HTTP.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Any

from config import (
    GEMINI_MODEL,
    GOOGLE_API_KEY,
    LLM_PROVIDER,
    VERTEX_AI_LOCATION,
    VERTEX_AI_PROJECT,
)
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

model: Any = None
COMBINED_TOOL_DEFS: list[dict] = list(CUSTOM_TOOL_DEFS)
MCP_TOOL_NAMES: set[str] = set()

_use_vertex = LLM_PROVIDER == "vertex_ai"


async def init_agent() -> None:
    global model, COMBINED_TOOL_DEFS, MCP_TOOL_NAMES

    if _use_vertex:
        _init_vertex()
    else:
        _init_ai_studio()

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

    tool_list = _build_google_tools()
    model = _create_model(tool_list)
    logger.info("Gemini model initialized (%s): %s with %d tools",
                LLM_PROVIDER, GEMINI_MODEL, len(COMBINED_TOOL_DEFS))


def _init_vertex() -> None:
    import vertexai
    project = VERTEX_AI_PROJECT or os.getenv("GOOGLE_CLOUD_PROJECT")
    if project:
        vertexai.init(project=project, location=VERTEX_AI_LOCATION)
        logger.info("Vertex AI initialized (project=%s, location=%s)", project, VERTEX_AI_LOCATION)
    else:
        vertexai.init(location=VERTEX_AI_LOCATION)
        logger.info("Vertex AI initialized with ADC (location=%s)", VERTEX_AI_LOCATION)


def _init_ai_studio() -> None:
    import google.generativeai as genai
    if not GOOGLE_API_KEY:
        logger.error("GOOGLE_API_KEY is not set. Agent will not function until it is configured.")
    else:
        genai.configure(api_key=GOOGLE_API_KEY)
        logger.info("Google AI Studio configured (model=%s)", GEMINI_MODEL)


def _create_model(tool_list: list) -> Any:
    if _use_vertex:
        from vertexai.preview.generative_models import GenerativeModel
        return GenerativeModel(
            model_name=GEMINI_MODEL,
            system_instruction=SYSTEM_PROMPT,
            tools=tool_list,
        )
    else:
        import google.generativeai as genai
        return genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            system_instruction=SYSTEM_PROMPT,
            tools=tool_list,
        )


async def close_agent() -> None:
    from mcp_bridge import close_mcp
    await close_mcp()


def agent_status() -> dict:
    return {
        "provider": LLM_PROVIDER,
        "model": GEMINI_MODEL,
        "llm": "connected" if model else "not configured",
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


def _build_google_tools() -> list:
    declarations = []
    if _use_vertex:
        from vertexai.preview.generative_models import FunctionDeclaration, Tool
    else:
        from google.generativeai.types import FunctionDeclaration, Tool
    for td in COMBINED_TOOL_DEFS:
        params = _sanitize_schema(dict(td["parameters"]))
        declarations.append(FunctionDeclaration(
            name=td["name"],
            description=td["description"],
            parameters=params,
        ))
    return [Tool(function_declarations=declarations)] if declarations else []


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


async def _generate_with_retry(
    contents: list,
    max_retries: int = 5,
    **kwargs,
) -> Any:
    last_error = None
    for attempt in range(max_retries):
        try:
            return await model.generate_content_async(contents=contents, **kwargs)
        except Exception as e:
            last_error = e
            error_str = str(e).lower()
            if "429" in error_str or "resource_exhausted" in error_str or "rate" in error_str:
                if attempt < max_retries - 1:
                    wait = (2 ** attempt) + (0.5 * attempt)
                    logger.warning("Rate limited — retrying in %.1fs (attempt %d/%d)", wait, attempt + 1, max_retries)
                    await asyncio.sleep(wait)
                    continue
            raise
    raise last_error


async def process_message(
    message: str,
    history: list[dict],
) -> tuple[str, dict | None, list[dict] | None]:
    if not model:
        provider_hint = "VERTEX_AI_PROJECT" if _use_vertex else "GOOGLE_API_KEY"
        return f"Agent is not configured. Please set {provider_hint} and restart.", None, None

    contents: list = []
    for msg in history:
        role = msg.get("role", "user")
        text = msg.get("text", msg.get("content", ""))
        if not text:
            continue
        g_role = "model" if role == "assistant" else "user"
        contents.append({"role": g_role, "parts": [{"text": text}]})

    contents.append({"role": "user", "parts": [{"text": message}]})

    tool_calls_log: list[dict] = []
    latest_plan_data: dict | None = None

    generation_config = {
        "temperature": 0.5,
        "max_output_tokens": 2048,
    }

    for turn in range(MAX_TOOL_TURNS):
        try:
            response = await _generate_with_retry(
                contents,
                generation_config=generation_config,
            )
        except Exception as e:
            logger.error("Gemini API call failed: %s", e, exc_info=True)
            return f"I'm sorry, I encountered an error: {e}", latest_plan_data, (tool_calls_log if tool_calls_log else None)

        if not response.candidates:
            logger.warning("No candidates returned by the model")
            return "I'm sorry, I couldn't process that request.", None, None

        candidate = response.candidates[0]
        function_calls = []
        text_parts = []
        for part in candidate.content.parts:
            if part.function_call:
                function_calls.append(part.function_call)
            if part.text:
                text_parts.append(part.text)

        if not function_calls:
            reply = "".join(text_parts).strip() or "Let me know how I can help with your World Cup trip!"
            return reply, latest_plan_data, (tool_calls_log if tool_calls_log else None)

        contents.append(candidate.content)

        function_response_parts = []
        for fc in function_calls:
            fc_name = fc.name
            fc_args = dict(fc.args) if fc.args else {}
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

            function_response_parts.append(_make_function_response(fc_name, tool_result))

        contents.append(_make_content(function_response_parts))

    return "Let me know if you'd like to refine the plan further!", latest_plan_data, tool_calls_log


def _make_function_response(name: str, response_data: dict) -> Any:
    if _use_vertex:
        from vertexai.preview.generative_models import Part
        return Part.from_function_response(name=name, response=response_data)
    else:
        from google.generativeai import protos
        return protos.Part(
            function_response=protos.FunctionResponse(
                name=name,
                response=response_data,
            )
        )


def _make_content(parts: list) -> Any:
    if _use_vertex:
        from vertexai.preview.generative_models import Content
        return Content(role="user", parts=parts)
    else:
        from google.generativeai import protos
        return protos.Content(role="user", parts=parts)
