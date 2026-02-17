---
name: dapr-invocation-pattern
description: Dapr service invocation pattern for FastAPI Todo app. Use DaprClient.invoke_method to call other services with user_id propagated via metadata. Use when implementing service-to-service communication in FastAPI applications with user context propagation.
---

# Dapr Service Invocation Pattern for FastAPI Todo App

## Overview

This skill provides guidance for implementing Dapr service invocation pattern in FastAPI applications. It helps integrate Dapr's service-to-service communication capabilities with proper user context propagation.

## Prerequisites

- Dapr runtime installed and running
- Dapr Python SDK (`pip install dapr`)
- Dapr service invocation configured
- FastAPI application with user authentication/authorization

## Implementation Pattern

### Import and Client Setup

```python
from dapr.clients import DaprClient
import json
import asyncio
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)
```

### Service Invocation Function

```python
async def invoke_service(
    app_id: str,
    method_name: str,
    data: Dict[str, Any],
    user_id: str,
    content_type: str = "application/json"
) -> Optional[Dict[str, Any]]:
    """
    Invoke a Dapr service with user context propagation.

    Args:
        app_id: The target application ID
        method_name: The method to invoke
        data: The payload to send
        user_id: The ID of the user triggering the invocation
        content_type: The content type of the request

    Returns:
        Response data from the service or None if failed
    """
    try:
        # Prepare the data
        payload = json.dumps(data) if isinstance(data, dict) else data

        with DaprClient() as dapr:
            response = await dapr.invoke_method(
                app_id=app_id,
                method_name=method_name,
                data=payload,
                content_type=content_type,
                metadata={
                    "user_id": str(user_id),
                    "content_type": content_type
                }
            )

        # Parse response
        response_data = json.loads(response.data.getvalue().decode('utf-8')) if response.data.getvalue() else {}

        logger.info(f"Successfully invoked service '{app_id}/{method_name}' for user '{user_id}'")
        return response_data

    except Exception as e:
        logger.error(f"Failed to invoke service '{app_id}/{method_name}': {str(e)}")
        return None
```

### Integration in FastAPI Endpoint

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter()

class ServiceInvocationRequest(BaseModel):
    app_id: str
    method_name: str
    data: Dict[str, Any]
    user_id: str

@router.post("/invoke-service")
async def service_invocation(
    request: ServiceInvocationRequest,
    current_user = Depends(get_current_user)
):
    """
    Example endpoint that invokes another service with user isolation.
    """
    response = await invoke_service(
        app_id=request.app_id,
        method_name=request.method_name,
        data=request.data,
        user_id=current_user.id
    )

    if response is None:
        raise HTTPException(status_code=500, detail="Failed to invoke service")

    return {"message": "Service invoked successfully", "response": response}
```

## Key Features

1. **User Context Propagation**: Always includes `user_id` in Dapr metadata for proper context propagation
2. **Async-Friendly**: Designed to work seamlessly with FastAPI's async architecture
3. **Error Handling**: Gracefully handles invocation failures without crashing endpoints
4. **Flexible**: Supports different content types and method names
5. **Secure**: Proper user context maintained in metadata

## Example Usage

```python
# In your FastAPI endpoint
payload = {
    "notification_type": "task_completed",
    "task_id": 123,
    "user_id": "user-456",
    "message": "Task has been completed successfully"
}

result = await invoke_service(
    app_id="notification-service",
    method_name="notify",
    data=payload,
    user_id="user-456"
)

if result:
    print("Notification sent successfully")
else:
    print("Failed to send notification")
```

## Alternative Direct Usage

```python
# Direct usage with DaprClient
async def direct_invoke_example(user_id: str):
    try:
        payload = json.dumps({
            "action": "send_email",
            "user_id": user_id,
            "email_content": "Welcome to our service!"
        })

        with DaprClient() as dapr:
            response = await dapr.invoke_method(
                app_id="email-service",
                method_name="send",
                data=payload,
                metadata={"user_id": str(user_id)}
            )

        return json.loads(response.data.getvalue().decode('utf-8'))
    except Exception as e:
        logger.error(f"Dapr invocation failed: {str(e)}")
        return None
```

## Best Practices

- Always validate the response from invoked services
- Implement appropriate timeouts for service invocations
- Use circuit breakers for resilient service-to-service communication
- Log both successful and failed invocations for monitoring
- Consider using Dapr's built-in retry mechanisms when appropriate