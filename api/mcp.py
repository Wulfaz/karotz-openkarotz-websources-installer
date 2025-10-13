"""
MCP Server Integration Design (On-Device)

This module handles requests for the Model Context Protocol (MCP) server.
It's designed to run on the Karotz device itself, translating MCP actions
into direct calls to the API's internal functions.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List, Coroutine

# Import the API functions directly from main.
# This avoids circular imports and allows direct function calls.
from . import main as karotz_api

mcp_router = APIRouter()

# 1. MCP Request and Response Models
class MCPRequest(BaseModel):
    actions: List[Dict[str, Any]]

class MCPResponse(BaseModel):
    results: List[Dict[str, Any]]


# 2. MCP Endpoint
@mcp_router.post("/mcp", response_model=MCPResponse, tags=["MCP"])
async def handle_mcp_request(request: MCPRequest):
    """
    Receives an MCP request and orchestrates the execution of actions
    by calling the internal API functions directly.
    """
    results = []
    for action_data in request.actions:
        result = await execute_karotz_action(action_data)
        results.append(result)

    return MCPResponse(results=results)


# 3. Action Execution Logic
async def execute_karotz_action(action_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes a single action by dispatching to the appropriate API function.
    """
    action_type = action_data.get("type")
    params = action_data.get("params", {})

    try:
        if action_type == "status.get":
            response = karotz_api.get_status()
            return {"action": action_type, "status": "success", "data": response}

        elif action_type == "leds.set":
            led_action = karotz_api.LedAction(**params)
            response = karotz_api.set_led(led_action)
            return {"action": action_type, "status": "success", "data": response}

        elif action_type == "ears.set":
            ear_action = karotz_api.EarsAction(**params)
            response = karotz_api.set_ears(ear_action)
            return {"action": action_type, "status": "success", "data": response}

        elif action_type == "device.reboot":
            response = karotz_api.reboot_device()
            return {"action": action_type, "status": "success", "data": response}

        elif action_type == "device.sleep":
            response = karotz_api.sleep_device()
            return {"action": action_type, "status": "success", "data": response}

        else:
            raise HTTPException(status_code=400, detail=f"Unknown action type: {action_type}")

    except HTTPException as e:
        return {"action": action_type, "status": "error", "details": e.detail}
    except Exception as e:
        # Catching potential Pydantic validation errors or other exceptions
        return {"action": action_type, "status": "error", "details": str(e)}