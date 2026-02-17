"""
AI Agent module for the Todo Chatbot.

This module integrates with Groq's API (OpenAI-compatible) to process natural language
requests and coordinate with MCP tools to perform task operations.
"""
import json
import logging
import time
from datetime import datetime, timezone
from typing import Tuple, List, Dict, Any
from sqlmodel import Session
from openai import OpenAI
from src.mcp_server.tools import (
    add_task_tool,
    list_tasks_tool,
    complete_task_tool,
    delete_task_tool,
    update_task_tool
)

logger = logging.getLogger(__name__)

# Initialize Groq client (OpenAI-compatible API) with request timeout
from src.core.config import settings
client = OpenAI(
    api_key=settings.groq_api_key,
    base_url="https://api.groq.com/openai/v1",
    timeout=30.0,  # 30-second timeout per request
)

# Tool dispatcher — maps function names to callables
TOOL_DISPATCH = {
    "add_task": add_task_tool,
    "list_tasks": list_tasks_tool,
    "complete_task": complete_task_tool,
    "delete_task": delete_task_tool,
    "update_task": update_task_tool,
}

# Model to use
MODEL_NAME = "llama-3.3-70b-versatile"
MAX_ITERATIONS = 5
MAX_RETRIES = 3


def _build_system_prompt(user_id: str) -> str:
    """Build the system prompt with current datetime and user context."""
    current_datetime_iso = datetime.now(timezone.utc).isoformat()

    return f"""You are a helpful AI assistant that manages a user's todo list.
You can help users add, list, update, delete, and complete tasks.
You have access to specific tools to perform these operations.

IMPORTANT: The current user's ID is: {user_id}
Always use this exact user_id value when calling any tool.

CURRENT DATE/TIME: {current_datetime_iso}
Use this to calculate relative dates like "in 1 minute", "tomorrow", "next week", etc.
For example, if the user says "due in 5 minutes", add 5 minutes to the current time and convert to ISO format.

CRITICAL RULES FOR TASK OPERATIONS:
1. When a user wants to DELETE, COMPLETE, or UPDATE a task by name/title:
   - FIRST call list_tasks to get all tasks and their IDs
   - THEN find the task that matches the user's description
   - ONLY THEN call the appropriate tool with the correct task_id
   - If no matching task is found, tell the user the task doesn't exist

2. When a user wants to add a task, use the add_task tool directly.

3. When a user wants to see their tasks, use the list_tasks tool.

4. NEVER guess task IDs. Always verify by listing tasks first.

5. Match tasks by title (case-insensitive, partial match is OK).

Tool usage:
- add_task: user_id="{user_id}", title, description (optional), priority, tags, due_date, recurrence_rule, reminder_enabled
- list_tasks: user_id="{user_id}", status (optional: "all", "pending", "completed"), priority, tags, sort_by, sort_order
- complete_task: user_id="{user_id}", task_id (integer)
- delete_task: user_id="{user_id}", task_id (integer)
- update_task: user_id="{user_id}", task_id (integer), title, description, priority, tags, due_date, recurrence_rule, reminder_enabled

PHASE V.1 FIELDS (all optional when creating/updating tasks):
- priority: "high", "medium", or "low"
- tags: list of tag names (e.g. ["work", "urgent"])
- due_date: ISO date string (e.g. "2025-06-15T09:00:00Z")
- recurrence_rule: DAILY, WEEKLY, MONTHLY, or YEARLY
- reminder_enabled: true/false

When listing tasks, you can filter by priority and tags, and sort by priority, due_date, title, or created_at.

Always respond in a friendly, helpful tone and confirm actions taken."""


def _build_tools() -> list:
    """Return the tool definitions for the AI model."""
    return [
        {
            "type": "function",
            "function": {
                "name": "add_task",
                "description": "Add a new task to the user's todo list with optional priority, tags, due date, recurrence, and reminders",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The user's ID"},
                        "title": {"type": "string", "description": "The title of the task"},
                        "description": {"type": "string", "description": "Optional description of the task"},
                        "priority": {"type": "string", "enum": ["high", "medium", "low"], "description": "Task priority level"},
                        "tags": {"type": "array", "items": {"type": "string"}, "description": "List of tag names to associate with the task"},
                        "due_date": {"type": "string", "description": "Due date in ISO format (e.g. 2025-06-15T09:00:00Z)"},
                        "recurrence_rule": {"type": "string", "enum": ["DAILY", "WEEKLY", "MONTHLY", "YEARLY"], "description": "Recurrence rule for repeating tasks"},
                        "reminder_enabled": {"type": "boolean", "description": "Whether to enable reminders for this task"}
                    },
                    "required": ["user_id", "title"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_tasks",
                "description": "List the user's tasks with optional filtering by status, priority, tags, and sorting",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The user's ID"},
                        "status": {"type": "string", "enum": ["all", "pending", "completed"], "description": "Filter by completion status"},
                        "priority": {"type": "string", "enum": ["high", "medium", "low"], "description": "Filter by priority level"},
                        "tags": {"type": "array", "items": {"type": "string"}, "description": "Filter by tag names (returns tasks matching any of the tags)"},
                        "sort_by": {"type": "string", "enum": ["created_at", "priority", "due_date", "title"], "description": "Field to sort by (default: created_at)"},
                        "sort_order": {"type": "string", "enum": ["asc", "desc"], "description": "Sort direction (default: desc)"}
                    },
                    "required": ["user_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "complete_task",
                "description": "Mark a task as complete",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The user's ID"},
                        "task_id": {"type": "integer", "description": "The ID of the task to complete"}
                    },
                    "required": ["user_id", "task_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_task",
                "description": "Delete a task from the user's list",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The user's ID"},
                        "task_id": {"type": "integer", "description": "The ID of the task to delete"}
                    },
                    "required": ["user_id", "task_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_task",
                "description": "Update a task's details including priority, tags, due date, recurrence, and reminders",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The user's ID"},
                        "task_id": {"type": "integer", "description": "The ID of the task to update"},
                        "title": {"type": "string", "description": "New title for the task"},
                        "description": {"type": "string", "description": "New description for the task"},
                        "priority": {"type": "string", "enum": ["high", "medium", "low"], "description": "New priority level"},
                        "tags": {"type": "array", "items": {"type": "string"}, "description": "New list of tag names (replaces existing tags)"},
                        "due_date": {"type": "string", "description": "New due date in ISO format (e.g. 2025-06-15T09:00:00Z)"},
                        "recurrence_rule": {"type": "string", "enum": ["DAILY", "WEEKLY", "MONTHLY", "YEARLY"], "description": "New recurrence rule"},
                        "reminder_enabled": {"type": "boolean", "description": "Whether to enable reminders"}
                    },
                    "required": ["user_id", "task_id"]
                }
            }
        }
    ]


def _call_groq(messages: list, tools: list = None, retry_label: str = "") -> Any:
    """
    Call Groq API with retry logic. Returns the API response or None on failure.

    Args:
        messages: Chat history messages
        tools: Tool definitions (None for tool-free calls)
        retry_label: Label for log messages (e.g., "iteration 1", "final")

    Returns:
        API response object or None if all retries failed
    """
    last_error = None

    for retry in range(MAX_RETRIES):
        try:
            kwargs = {
                "model": MODEL_NAME,
                "messages": messages,
            }
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"

            response = client.chat.completions.create(**kwargs)
            return response

        except Exception as e:
            last_error = e
            error_str = str(e)
            logger.warning(
                "Groq API call failed [%s] (attempt %d/%d): %s",
                retry_label, retry + 1, MAX_RETRIES, error_str
            )

            # Don't retry on tool format errors
            if "tool_use_failed" in error_str:
                return None

            if retry < MAX_RETRIES - 1:
                time.sleep(0.5 * (retry + 1))

    logger.error(
        "Groq API call exhausted all retries [%s]: %s",
        retry_label, str(last_error)
    )
    return None


def _execute_tool_calls(tool_calls: list, user_id: str) -> list:
    """Execute tool calls and return results."""
    results = []
    for tool_call in tool_calls:
        try:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            tool_call_id = tool_call.id

            # Ensure user_id is always present
            if "user_id" not in function_args:
                function_args["user_id"] = user_id

            # Dispatch to the correct tool
            handler = TOOL_DISPATCH.get(function_name)
            if handler:
                result = handler(**function_args)
            else:
                result = {"error": f"Unknown function: {function_name}"}

            logger.info("Tool executed: %s → %s", function_name, result.get("status", "ok") if isinstance(result, dict) else "ok")

            results.append({
                "tool_call_id": tool_call_id,
                "name": function_name,
                "arguments": function_args,
                "result": result
            })
        except Exception as e:
            logger.error("Tool execution failed: %s — %s", function_name if 'function_name' in dir() else "unknown", str(e))
            results.append({
                "tool_call_id": getattr(tool_call, 'id', 'unknown'),
                "name": function_name if 'function_name' in locals() else "unknown",
                "arguments": {},
                "result": {"error": f"Error executing tool: {str(e)}"}
            })
    return results


def _build_success_fallback(tool_results: list) -> str:
    """
    Build a friendly response from tool results when the AI can't generate one.
    This ensures the user sees confirmation even if the second Groq call fails.
    """
    parts = []
    for tr in tool_results:
        name = tr.get("name", "")
        result = tr.get("result", {})

        if isinstance(result, dict):
            status = result.get("status", "")
            title = result.get("title", "")
            error = result.get("error")

            if error:
                parts.append(f"Error: {error}")
            elif name == "add_task" and status == "created":
                due = result.get("due_date", "")
                due_str = f" (due: {due})" if due else ""
                parts.append(f"Task \"{title}\" has been created{due_str}.")
            elif name == "complete_task":
                parts.append(f"Task \"{title}\" has been marked as {status}.")
            elif name == "delete_task":
                parts.append(f"Task \"{title}\" has been deleted.")
            elif name == "update_task":
                parts.append(f"Task \"{title}\" has been updated.")
            else:
                parts.append(f"Done: {name}")
        elif isinstance(result, list):
            count = len(result)
            parts.append(f"Found {count} task{'s' if count != 1 else ''}.")

    return " ".join(parts) if parts else "I've completed the requested operation."


def process_chat_request(
    user_id: str,
    conversation_id: int,
    user_message: str,
    session: Session
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Process a chat request using AI and MCP tools.

    Args:
        user_id: The ID of the requesting user
        conversation_id: The ID of the conversation
        user_message: The user's natural language message
        session: Database session for retrieving conversation history

    Returns:
        Tuple of (AI response text, list of tool call results)
    """
    try:
        # Get conversation history
        from src.services.conversation_service import ConversationService

        messages = ConversationService.get_messages_for_conversation(
            session=session,
            conversation_id=conversation_id,
            user_id=user_id
        )

        # Build chat history
        chat_history = [
            {"role": "system", "content": _build_system_prompt(user_id)}
        ]

        # Add prior conversation messages (exclude the current one, already in DB)
        for msg in messages[:-1]:
            chat_history.append({"role": msg.role, "content": msg.content})

        # Add current user message
        chat_history.append({"role": "user", "content": user_message})

        tools = _build_tools()
        all_tool_call_results = []

        # Multi-turn tool calling loop
        for iteration in range(MAX_ITERATIONS):
            response = _call_groq(
                messages=chat_history,
                tools=tools,
                retry_label=f"iteration {iteration + 1}"
            )

            if response is None:
                # API failed — if we already executed tools, return a success summary
                if all_tool_call_results:
                    logger.warning(
                        "Groq API failed after tools executed; returning fallback summary"
                    )
                    return _build_success_fallback(all_tool_call_results), all_tool_call_results

                # No tools executed yet — try without tools as fallback
                logger.warning("Groq API failed on first call; trying without tools")
                fallback = _call_groq(
                    messages=chat_history,
                    tools=None,
                    retry_label="fallback (no tools)"
                )
                if fallback:
                    return fallback.choices[0].message.content or "I'm not sure how to help with that.", []

                return (
                    "I'm having trouble connecting to the AI service right now. "
                    "Please try again in a moment, or use the Tasks page to manage your tasks directly."
                ), [{"error": "All API calls failed"}]

            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            # No tool calls — we have our final text response
            if not tool_calls:
                ai_response = response_message.content
                if not ai_response:
                    ai_response = "I'm not sure how to help with that. Could you please rephrase?"
                return ai_response, all_tool_call_results

            # Execute tool calls
            tool_results = _execute_tool_calls(tool_calls, user_id)
            all_tool_call_results.extend(tool_results)

            # Append assistant message (with tool_calls) and tool results to history
            chat_history.append(response_message)
            for tr in tool_results:
                chat_history.append({
                    "role": "tool",
                    "tool_call_id": tr["tool_call_id"],
                    "content": json.dumps(tr["result"])
                })

        # Exhausted iterations — get final summary from AI
        final_response = _call_groq(
            messages=chat_history,
            tools=None,
            retry_label="final summary"
        )

        if final_response:
            ai_response = final_response.choices[0].message.content
            if ai_response:
                return ai_response, all_tool_call_results

        # AI can't summarize — build our own from tool results
        return _build_success_fallback(all_tool_call_results), all_tool_call_results

    except Exception as e:
        logger.error("Unexpected error in process_chat_request: %s", str(e), exc_info=True)
        return (
            f"Sorry, I encountered an unexpected error: {str(e)}",
            [{"error": f"Unexpected error: {str(e)}"}]
        )
