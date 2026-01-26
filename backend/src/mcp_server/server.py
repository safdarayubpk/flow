"""
MCP (Model Context Protocol) Server for the AI Todo Chatbot.

This module implements an MCP server that exposes task operations as tools
that can be called by AI agents.
"""
import asyncio
from typing import Dict, Any, List
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.shared.exceptions import McpError
from .tools import (
    add_task_tool,
    list_tasks_tool,
    complete_task_tool,
    delete_task_tool,
    update_task_tool
)


# Create the MCP server instance
server = Server("todo-mcp-server")


@server.after_initialization
async def init_logging(context):
    """Initialize logging after server initialization."""
    print("MCP Server initialized for Todo Chatbot")


@server.call("tools/add_task")
async def handle_add_task(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle the add_task tool call from AI agents.

    Expected params:
    - user_id: str
    - title: str
    - description: str (optional)
    """
    try:
        user_id = params["user_id"]
        title = params["title"]
        description = params.get("description")

        result = add_task_tool(user_id=user_id, title=title, description=description)
        return {"result": result}
    except KeyError as e:
        raise McpError(f"Missing required parameter: {e}")
    except Exception as e:
        raise McpError(f"Error in add_task: {str(e)}")


@server.call("tools/list_tasks")
async def handle_list_tasks(params: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Handle the list_tasks tool call from AI agents.

    Expected params:
    - user_id: str
    - status: str (optional, default: "all")
    """
    try:
        user_id = params["user_id"]
        status = params.get("status", "all")

        result = list_tasks_tool(user_id=user_id, status=status)
        return {"result": result}
    except KeyError as e:
        raise McpError(f"Missing required parameter: {e}")
    except Exception as e:
        raise McpError(f"Error in list_tasks: {str(e)}")


@server.call("tools/complete_task")
async def handle_complete_task(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle the complete_task tool call from AI agents.

    Expected params:
    - user_id: str
    - task_id: int
    """
    try:
        user_id = params["user_id"]
        task_id = params["task_id"]

        result = complete_task_tool(user_id=user_id, task_id=task_id)
        return {"result": result}
    except KeyError as e:
        raise McpError(f"Missing required parameter: {e}")
    except Exception as e:
        raise McpError(f"Error in complete_task: {str(e)}")


@server.call("tools/delete_task")
async def handle_delete_task(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle the delete_task tool call from AI agents.

    Expected params:
    - user_id: str
    - task_id: int
    """
    try:
        user_id = params["user_id"]
        task_id = params["task_id"]

        result = delete_task_tool(user_id=user_id, task_id=task_id)
        return {"result": result}
    except KeyError as e:
        raise McpError(f"Missing required parameter: {e}")
    except Exception as e:
        raise McpError(f"Error in delete_task: {str(e)}")


@server.call("tools/update_task")
async def handle_update_task(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle the update_task tool call from AI agents.

    Expected params:
    - user_id: str
    - task_id: int
    - title: str (optional)
    - description: str (optional)
    """
    try:
        user_id = params["user_id"]
        task_id = params["task_id"]
        title = params.get("title")
        description = params.get("description")

        result = update_task_tool(
            user_id=user_id,
            task_id=task_id,
            title=title,
            description=description
        )
        return {"result": result}
    except KeyError as e:
        raise McpError(f"Missing required parameter: {e}")
    except Exception as e:
        raise McpError(f"Error in update_task: {str(e)}")


@server.list_prompts()
async def list_prompts() -> List[Dict[str, Any]]:
    """Return a list of available prompts."""
    return []


@server.get_prompt()
async def get_prompt(name: str) -> Dict[str, Any]:
    """Return a specific prompt by name."""
    raise McpError(f"Prompt '{name}' not found")


async def run_mcp_server(host: str = "127.0.0.1", port: int = 8080):
    """Run the MCP server."""
    from mcp.server.stdio import stdio_server

    options = InitializationOptions(
        server_name="todo-mcp-server",
        server_version="1.0.0"
    )

    async with stdio_server(server, options) as s:
        await s.wait_for_shutdown()


if __name__ == "__main__":
    asyncio.run(run_mcp_server())