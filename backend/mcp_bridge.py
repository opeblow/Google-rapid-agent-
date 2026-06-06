from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Any

from config import DATABASE_NAME, MONGODB_URI

logger = logging.getLogger(__name__)

MCP_SESSION: Any = None
MCP_TOOLS: list[dict] = []
MCP_AVAILABLE = False
MCP_TRANSPORT_CTX: Any = None
MCP_SESSION_CTX: Any = None


MCP_INIT_TIMEOUT = 30.0
MCP_CALL_TIMEOUT = 15.0


async def init_mcp() -> bool:
    global MCP_SESSION, MCP_TOOLS, MCP_AVAILABLE, MCP_TRANSPORT_CTX, MCP_SESSION_CTX

    if not MONGODB_URI or MONGODB_URI == "mongodb://localhost:27017":
        logger.info("MCP bridge skipped — using default local MongoDB (no Atlas)")
        MCP_AVAILABLE = False
        return False

    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        # Run the MCP server READ-ONLY: the agent may query the database but must never
        # mutate it. Trip plans are persisted through the controlled save_plan tool, not
        # raw MCP writes — this prevents the model from corrupting the source match data.
        server_params = StdioServerParameters(
            command="npx",
            args=["-y", "mongodb-mcp-server@latest", "--readOnly"],
            env={
                **os.environ,
                "MONGODB_CONNECTION_STRING": MONGODB_URI,
                "MONGODB_DATABASE_NAME": DATABASE_NAME,
                "MDB_MCP_READ_ONLY": "true",
            },
        )

        MCP_TRANSPORT_CTX = stdio_client(server_params)
        read, write = await asyncio.wait_for(
            MCP_TRANSPORT_CTX.__aenter__(), timeout=MCP_INIT_TIMEOUT
        )

        MCP_SESSION_CTX = ClientSession(read, write)
        MCP_SESSION = await asyncio.wait_for(
            MCP_SESSION_CTX.__aenter__(), timeout=MCP_INIT_TIMEOUT
        )
        await asyncio.wait_for(MCP_SESSION.initialize(), timeout=MCP_INIT_TIMEOUT)

        tools_result = await asyncio.wait_for(
            MCP_SESSION.list_tools(), timeout=MCP_INIT_TIMEOUT
        )

        MCP_TOOLS = [
            {
                "name": f"mcp_{t.name.replace('-', '_')}",
                "original_name": t.name,
                "description": t.description or f"MongoDB {t.name}",
                "parameters": t.inputSchema or {"type": "object", "properties": {}},
            }
            for t in tools_result.tools
        ]
        MCP_AVAILABLE = True
        logger.info("MCP bridge ready — %d tools from MongoDB MCP Server", len(MCP_TOOLS))
        return True

    except asyncio.TimeoutError:
        logger.warning("MCP bridge initialization timed out after %ds", MCP_INIT_TIMEOUT)
    except FileNotFoundError:
        logger.warning("MCP bridge unavailable — 'npx' not found. Install Node.js for MCP integration.")
    except Exception as e:
        logger.warning("MCP bridge unavailable — %s: %s", type(e).__name__, e)

    MCP_SESSION = None
    MCP_TOOLS = []
    MCP_AVAILABLE = False
    return False


def get_mcp_function_definitions() -> list[dict]:
    if not MCP_AVAILABLE:
        return []
    return [
        {
            "name": t["name"],
            "description": t["description"],
            "parameters": t["parameters"],
        }
        for t in MCP_TOOLS
    ]


async def call_mcp_tool(gemini_name: str, args: dict) -> dict:
    if not MCP_SESSION:
        return {"error": "MongoDB MCP Server is not connected."}

    tool = next((t for t in MCP_TOOLS if t["name"] == gemini_name), None)
    if not tool:
        return {"error": f"Unknown MCP tool: {gemini_name}"}

    try:
        result = await asyncio.wait_for(
            MCP_SESSION.call_tool(tool["original_name"], args),
            timeout=MCP_CALL_TIMEOUT,
        )
        if result.isError:
            error_text = result.content[0].text if result.content else "Unknown error"
            logger.error("MCP tool '%s' returned error: %s", tool["original_name"], error_text)
            return {"error": error_text}

        texts = []
        for item in (result.content or []):
            if hasattr(item, "text") and item.text:
                texts.append(item.text)
            elif hasattr(item, "data") and item.data:
                texts.append(str(item.data))

        output = "\n".join(texts) if texts else str(result)
        try:
            parsed = json.loads(output)
            return {"result": parsed}
        except (json.JSONDecodeError, ValueError):
            return {"result": output}

    except Exception as e:
        logger.error("MCP call failed: %s(%s) — %s", tool["original_name"], args, e, exc_info=True)
        return {"error": f"MCP call failed: {e}"}


async def close_mcp():
    global MCP_SESSION, MCP_AVAILABLE, MCP_TRANSPORT_CTX, MCP_SESSION_CTX
    if MCP_SESSION and MCP_SESSION_CTX:
        try:
            await asyncio.wait_for(MCP_SESSION_CTX.__aexit__(None, None, None), timeout=10)
        except Exception:
            pass
    if MCP_TRANSPORT_CTX:
        try:
            await asyncio.wait_for(MCP_TRANSPORT_CTX.__aexit__(None, None, None), timeout=10)
        except Exception:
            pass
    MCP_SESSION = None
    MCP_SESSION_CTX = None
    MCP_TRANSPORT_CTX = None
    MCP_AVAILABLE = False
    logger.info("MCP session closed")
