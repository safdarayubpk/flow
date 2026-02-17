---
name: dapr-pubsub-pattern
description: Dapr pub/sub pattern for FastAPI Todo app with user isolation. Use Dapr Python SDK (dapr.clients.DaprClient) to publish events to pubsub component named "kafka-pubsub" with user_id in metadata. Use when implementing event publishing to Dapr pub/sub from FastAPI endpoints with user context propagation.
---

# Dapr Pub/Sub Pattern for FastAPI Todo App

## Overview

This skill provides guidance for implementing Dapr pub/sub pattern in FastAPI applications with user isolation. It helps integrate Dapr's distributed pub/sub capabilities with proper user context propagation.

## Prerequisites

- Dapr runtime installed and running
- Dapr Python SDK (`pip install dapr`)
- Dapr pubsub component named "kafka-pubsub" configured separately
- FastAPI application with user authentication/authorization

## Implementation Pattern

### Import and Client Setup

```python
from dapr.clients import DaprClient
import json
import asyncio
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)
```

### Event Publishing Function

```python
async def publish_todo_event(topic_name: str, event_data: Dict[str, Any], user_id: str) -> bool:
    """
    Publish an event to Dapr pub/sub with user context.

    Args:
        topic_name: The topic to publish to
        event_data: The event payload
        user_id: The ID of the user triggering the event

    Returns:
        True if published successfully, False otherwise
    """
    try:
        # Serialize the event data
        event_json = json.dumps(event_data)

        with DaprClient() as dapr:
            await dapr.publish_event(
                pubsub_name="kafka-pubsub",
                topic_name=topic_name,
                data=event_json,
                metadata={
                    "user_id": str(user_id),
                    "content_type": "application/json"
                }
            )

        logger.info(f"Event published to topic '{topic_name}' for user '{user_id}'")
        return True

    except Exception as e:
        logger.error(f"Failed to publish event to topic '{topic_name}': {str(e)}")
        return False
```

### Integration in FastAPI Endpoint

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter()

class TodoEvent(BaseModel):
    action: str
    task_id: int
    user_id: str
    details: Dict[str, Any] = {}

@router.post("/todos/{task_id}/trigger-event")
async def trigger_todo_event(task_id: int, event: TodoEvent, current_user = Depends(get_current_user)):
    """
    Example endpoint that publishes a todo event with user isolation.
    """
    success = await publish_todo_event(
        topic_name="todo-events",
        event_data=event.dict(),
        user_id=current_user.id
    )

    if not success:
        raise HTTPException(status_code=500, detail="Failed to publish event")

    return {"message": "Event published successfully", "success": True}
```

## Key Features

1. **User Isolation**: Always includes `user_id` in Dapr metadata for proper context propagation
2. **Async-Friendly**: Designed to work seamlessly with FastAPI's async architecture
3. **Error Handling**: Gracefully handles publishing failures without crashing endpoints
4. **Security**: Proper user context maintained in metadata
5. **Minimal Overhead**: Lightweight implementation focused on core functionality

## Example Usage

```python
# In your FastAPI endpoint
event_payload = {
    "action": "task_created",
    "task_id": 123,
    "user_id": "user-456",
    "details": {
        "title": "Sample task",
        "priority": "high"
    }
}

await publish_todo_event(
    topic_name="todo-events",
    event_data=event_payload,
    user_id="user-456"
)
```

## Configuration Notes

- The "kafka-pubsub" component must be configured separately in Dapr
- Ensure Dapr sidecar is running alongside your FastAPI application
- Configure appropriate retry and dead letter queue policies in your Dapr component
- Monitor Dapr sidecar logs for pub/sub connectivity issues