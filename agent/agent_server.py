from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from functools import partial
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import GEMINI_API_KEY
from tools import TOOL_DEFINITIONS as CUSTOM_TOOL_DEFS
from tools import TOOL_REGISTRY as CUSTOM_TOOL_REGISTRY

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger("agent_server")

SYSTEM_PROMPT = (
    "You are an AI travel agent for the 2026 FIFA World Cup across USA, Canada, and Mexico. "
    "Your job is to plan the perfect trip for fans.\n\n"
    "=== REAL 2026 FIFA WORLD CUP GROUPS ===\n"
    "Group A: Mexico, South Korea, Czech Republic, South Africa\n"
    "Group B: Canada, Qatar, Switzerland, Bosnia & Herzegovina\n"
    "Group C: Brazil, Morocco, Haiti, Scotland\n"
    "Group D: USA, Australia, Turkey, Paraguay\n"
    "Group E: Germany, Ecuador, Curacao, Ivory Coast\n"
    "Group F: Netherlands, Japan, Sweden, Tunisia\n"
    "Group G: Belgium, Iran, New Zealand, Egypt\n"
    "Group H: Spain, Saudi Arabia, Uruguay, Cape Verde\n"
    "Group I: France, Senegal, Iraq, Norway\n"
    "Group J: Argentina, Algeria, Austria, Jordan\n"
    "Group K: Portugal, DR Congo, Uzbekistan, Colombia\n"
    "Group L: England, Croatia, Ghana, Panama\n\n"
    "=== 16 HOST VENUES ===\n"
    "USA: Mercedes-Benz Stadium (Atlanta), Gillette Stadium (Boston), AT&T Stadium (Dallas), "
    "NRG Stadium (Houston), Arrowhead Stadium (Kansas City), SoFi Stadium (Los Angeles), "
    "Hard Rock Stadium (Miami), MetLife Stadium (New York/New Jersey), "
    "Lincoln Financial Field (Philadelphia), Levi's Stadium (San Francisco Bay Area), "
    "Lumen Field (Seattle)\n"
    "Canada: BMO Field (Toronto), BC Place (Vancouver)\n"
    "Mexico: Estadio Akron (Guadalajara), Estadio Azteca (Mexico City), Estadio BBVA (Monterrey)\n\n"
    "You MUST use the search_matches() tool to look up real match information by team, city, or date. "
    "After building or updating a trip plan, ALWAYS call save_plan() with the complete data "
    "(matches, hotels, budget, transport, daily schedule). "
    "You have 4 domain tools: search_matches, save_plan, get_plan, update_plan.\n\n"
    "Be enthusiastic — this is the World Cup!"
)

MAX_TOOL_TURNS = 6

client: Any = None
COMBINED_TOOL_DEFS: list[dict] = list(CUSTOM_TOOL_DEFS)
MCP_TOOL_NAMES: set[str] = set()


class AgentRequest(BaseModel):
    message: str
    history: list[dict] = []


class AgentResponse(BaseModel):
    reply: str
    plan_data: dict | None = None
    tool_calls: list[dict] | None = None
    mcp_enabled: bool = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    global client, COMBINED_TOOL_DEFS, MCP_TOOL_NAMES

    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY is not set. Agent will not function until it is configured.")
    else:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
        logger.info("Gemini client initialized")

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

    yield

    from mcp_bridge import close_mcp
    await close_mcp()
    from db import close as close_db
    close_db()
    logger.info("Agent server shut down")


app = FastAPI(title="World Cup 2026 Fan Agent", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


def _build_gemini_tools():
    if not client:
        return None
    from google.genai import types

    function_declarations = []
    for td in COMBINED_TOOL_DEFS:
        # Deep sanitize parameters to keep only Gemini-compatible schema
        params = _sanitize_schema(dict(td["parameters"]))
        
        function_declarations.append(
            types.FunctionDeclaration(
                name=td["name"],
                description=td["description"],
                parameters=params,
            )
        )
    return [types.Tool(function_declarations=function_declarations)]


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


async def _process_with_gemini(
    message: str,
    history: list[dict],
) -> tuple[str, dict | None, list[dict] | None]:
    if not client:
        return "Agent is not configured. Please set GEMINI_API_KEY and restart.", None, None

    from google.genai import types

    gemini_tools = _build_gemini_tools()

    contents: list[types.Content] = []
    for msg in history:
        role = "user" if msg.get("role") == "user" else "model"
        text = msg.get("text", msg.get("content", ""))
        if text:
            contents.append(types.Content(role=role, parts=[types.Part(text=text)]))

    contents.append(types.Content(role="user", parts=[types.Part(text=message)]))

    tool_calls_log: list[dict] = []
    latest_plan_data: dict | None = None
    loop = asyncio.get_running_loop()

    for turn in range(MAX_TOOL_TURNS):
        try:
            raw = await loop.run_in_executor(
                None,
                partial(
                    client.models.generate_content,
                    model="gemini-flash-latest",
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        tools=gemini_tools,
                        temperature=0.5,
                        max_output_tokens=4096,
                    ),
                ),
            )
        except Exception as e:
            logger.error("Gemini API call failed: %s", e, exc_info=True)
            return f"I'm sorry, I encountered an error communicating with the AI service: {e}", latest_plan_data, (tool_calls_log if tool_calls_log else None)

        if not raw.candidates:
            logger.warning("No candidates returned by Gemini (safety block?)")
            return "I'm sorry, I couldn't process that request due to content restrictions.", None, None

        candidate = raw.candidates[0]
        if not candidate.content or not candidate.content.parts:
            return raw.text or "I'm sorry, I couldn't generate a response.", None, None

        contents.append(candidate.content)

        function_calls = [p for p in candidate.content.parts if p.function_call]
        text_parts = [p.text for p in candidate.content.parts if p.text]

        if not function_calls:
            reply = "".join(text_parts) or "Let me know how I can help with your World Cup trip!"
            return reply, latest_plan_data, (tool_calls_log if tool_calls_log else None)

        for fc in function_calls:
            fc_name = fc.function_call.name
            fc_args = dict(fc.function_call.args) if fc.function_call.args else {}
            logger.info("Turn %d — Gemini called: %s(%s)", turn + 1, fc_name, fc_args)

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

            response_part = types.Part.from_function_response(
                name=fc_name,
                response=tool_result,
            )
            contents.append(types.Content(role="function", parts=[response_part]))

    return "Let me know if you'd like to refine the plan further!", latest_plan_data, tool_calls_log


@app.post("/agent/process", response_model=AgentResponse)
async def process_message(request: AgentRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    logger.info("Processing message (history: %d turns)", len(request.history))
    reply, plan_data, tool_calls = await _process_with_gemini(request.message, request.history)
    logger.info(
        "Reply: %d chars | plan: %s | tools: %d | mcp: %s",
        len(reply),
        "yes" if plan_data else "no",
        len(tool_calls) if tool_calls else 0,
        bool(MCP_TOOL_NAMES),
    )
    return AgentResponse(
        reply=reply,
        plan_data=plan_data,
        tool_calls=tool_calls,
        mcp_enabled=bool(MCP_TOOL_NAMES),
    )


@app.get("/agent/health")
async def health():
    return {
        "status": "ok" if client else "degraded",
        "gemini": "connected" if client else "not configured",
        "mcp": f"enabled ({len(MCP_TOOL_NAMES)} tools)" if MCP_TOOL_NAMES else "disabled",
        "custom_tools": len(CUSTOM_TOOL_DEFS),
        "total_tools": len(COMBINED_TOOL_DEFS),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("agent_server:app", host="0.0.0.0", port=8001, reload=True)
