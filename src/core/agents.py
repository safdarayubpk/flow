"""
AI Agent module for the Todo Chatbot.

This module integrates with OpenAI's API to process natural language
requests and coordinate with MCP tools to perform task operations.
"""
import os
import json
import time
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


# Initialize Groq client (OpenAI-compatible API)
from src.core.config import settings
client = OpenAI(
    api_key=settings.groq_api_key,
    base_url="https://api.groq.com/openai/v1"
)


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
        Tuple of (AI response, list of tool calls made)
    """
    try:
        # Get conversation history to provide context
        from src.services.conversation_service import ConversationService

        messages = ConversationService.get_messages_for_conversation(
            session=session,
            conversation_id=conversation_id,
            user_id=user_id
        )

        # Build the message history for the AI
        chat_history = []

        # Add system message to guide the AI
        chat_history.append({
            "role": "system",
            "content": f"""You are a helpful AI assistant that manages a user's todo list.
You can help users add, list, update, delete, and complete tasks.
You have access to specific tools to perform these operations.

IMPORTANT: The current user's ID is: {user_id}
Always use this exact user_id value when calling any tool.

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
- add_task: user_id="{user_id}", title, description (optional)
- list_tasks: user_id="{user_id}", status (optional: "all", "pending", "completed")
- complete_task: user_id="{user_id}", task_id (integer)
- delete_task: user_id="{user_id}", task_id (integer)
- update_task: user_id="{user_id}", task_id (integer), title/description (optional)

Always respond in a friendly, helpful tone and confirm actions taken."""
        })

        # Add conversation history
        for msg in messages[:-1]:  # Exclude the current message
            chat_history.append({
                "role": msg.role,
                "content": msg.content
            })

        # Add the current user message
        chat_history.append({
            "role": "user",
            "content": user_message
        })

        # Define the tools available to the AI
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "add_task",
                    "description": "Add a new task to the user's todo list",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "description": "The user's ID"},
                            "title": {"type": "string", "description": "The title of the task"},
                            "description": {"type": "string", "description": "Optional description of the task"}
                        },
                        "required": ["user_id", "title"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_tasks",
                    "description": "List the user's tasks with optional filtering",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "description": "The user's ID"},
                            "status": {"type": "string", "description": "Filter by status: all, pending, or completed"}
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
                    "description": "Update a task's details",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "description": "The user's ID"},
                            "task_id": {"type": "integer", "description": "The ID of the task to update"},
                            "title": {"type": "string", "description": "New title for the task (optional)"},
                            "description": {"type": "string", "description": "New description for the task (optional)"}
                        },
                        "required": ["user_id", "task_id"]
                    }
                }
            }
        ]

        # Multi-turn tool calling loop (max 5 iterations to prevent infinite loops)
        max_iterations = 5
        max_retries = 3  # Retry logic for API failures
        all_tool_call_results = []

        # Model to use - llama-3.3-70b-versatile is the recommended production model
        model_name = "llama-3.3-70b-versatile"

        for iteration in range(max_iterations):
            # Call the API with tools (with retry logic)
            response = None
            last_error = None
            tool_use_failed = False

            for retry in range(max_retries):
                try:
                    response = client.chat.completions.create(
                        model=model_name,
                        messages=chat_history,
                        tools=tools,
                        tool_choice="auto"
                    )
                    break  # Success, exit retry loop
                except Exception as e:
                    last_error = e
                    error_str = str(e)

                    # Check if it's a tool_use_failed error
                    if "tool_use_failed" in error_str:
                        tool_use_failed = True
                        break  # Don't retry on tool format errors

                    if retry < max_retries - 1:
                        time.sleep(0.5 * (retry + 1))  # Backoff: 0.5s, 1s, 1.5s
                    continue

            # If tool use failed, try without tools as fallback
            if tool_use_failed and response is None:
                try:
                    # Fallback: Ask the model to respond naturally without tools
                    fallback_messages = chat_history.copy()
                    fallback_messages[0] = {
                        "role": "system",
                        "content": f"""You are a helpful AI assistant that manages a user's todo list.
The user wants to perform a task operation. Please acknowledge their request and let them know
you're having temporary technical difficulties with the task management system.
Ask them to try again in a moment, or suggest they use the Tasks page directly to:
- View tasks at /tasks
- Add, edit, delete, or complete tasks using the buttons on that page

Be friendly and apologetic about the inconvenience."""
                    }
                    response = client.chat.completions.create(
                        model=model_name,
                        messages=fallback_messages
                    )
                    ai_response = response.choices[0].message.content
                    return ai_response, [{"info": "Used fallback response due to tool calling issue"}]
                except Exception as fallback_error:
                    return "I'm having trouble processing task operations right now. Please try using the Tasks page directly to manage your tasks, or try again in a moment.", [{"error": f"Fallback also failed: {str(fallback_error)}"}]

            if response is None:
                error_msg = f"Sorry, I'm currently experiencing issues processing your request. Please try again later."
                return error_msg, [{"error": f"API error after {max_retries} retries: {str(last_error)}"}]

            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            # If no tool calls, we have our final response
            if not tool_calls:
                ai_response = response_message.content
                if not ai_response:
                    ai_response = "I'm not sure how to help with that. Could you please rephrase?"
                return ai_response, all_tool_call_results

            # Execute the tool calls
            tool_call_results = []
            for tool_call in tool_calls:
                try:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    tool_call_id = tool_call.id

                    # Add the user_id to the function args if not present
                    if "user_id" not in function_args:
                        function_args["user_id"] = user_id

                    # Execute the appropriate tool
                    if function_name == "add_task":
                        result = add_task_tool(**function_args)
                    elif function_name == "list_tasks":
                        result = list_tasks_tool(**function_args)
                    elif function_name == "complete_task":
                        result = complete_task_tool(**function_args)
                    elif function_name == "delete_task":
                        result = delete_task_tool(**function_args)
                    elif function_name == "update_task":
                        result = update_task_tool(**function_args)
                    else:
                        result = {"error": f"Unknown function: {function_name}"}

                    tool_call_results.append({
                        "tool_call_id": tool_call_id,
                        "name": function_name,
                        "arguments": function_args,
                        "result": result
                    })
                except Exception as e:
                    tool_call_results.append({
                        "tool_call_id": tool_call.id if hasattr(tool_call, 'id') else "unknown",
                        "name": function_name if 'function_name' in locals() else "unknown",
                        "arguments": {},
                        "result": {"error": f"Error executing tool: {str(e)}"}
                    })

            # Add tool calls and results to chat history for next iteration
            chat_history.append(response_message)
            for tool_call_result in tool_call_results:
                chat_history.append({
                    "role": "tool",
                    "tool_call_id": tool_call_result["tool_call_id"],
                    "content": json.dumps(tool_call_result["result"])
                })

            # Accumulate all tool call results
            all_tool_call_results.extend(tool_call_results)

        # If we've exhausted iterations, get a final response (with retry)
        ai_response = "I've completed the requested operations."
        for retry in range(max_retries):
            try:
                final_response = client.chat.completions.create(
                    model=model_name,
                    messages=chat_history
                )
                ai_response = final_response.choices[0].message.content
                break
            except Exception as e:
                if retry < max_retries - 1:
                    time.sleep(0.5 * (retry + 1))
                continue

        return ai_response, all_tool_call_results

    except Exception as e:
        # Handle any unexpected errors gracefully
        error_msg = f"Sorry, I encountered an unexpected error processing your request: {str(e)}"
        return error_msg, [{"error": f"Unexpected error: {str(e)}"}]