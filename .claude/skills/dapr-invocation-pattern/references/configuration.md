# Dapr Service Invocation Configuration

## Dapr Sidecar Configuration

To use this skill, ensure your Dapr sidecar is properly configured. Here's an example configuration:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: appconfig
spec:
  tracing:
    samplingRate: "1"
    zipkin:
      endpointAddress: "http://zipkin.default.svc.cluster.local:9411/api/v2/spans"
  metric:
    enabled: true
  httpPipeline:
    handlers:
    - name: validator
      type: middleware.http.validator
```

## Complete FastAPI Integration Example

```python
from fastapi import FastAPI, Depends, HTTPException
from dapr.clients import DaprClient
import json
import logging
from typing import Dict, Any
from pydantic import BaseModel

app = FastAPI()
logger = logging.getLogger(__name__)

class ServiceCallRequest(BaseModel):
    app_id: str
    method_name: str
    data: Dict[str, Any]
    user_id: str

async def invoke_service_with_context(
    app_id: str,
    method_name: str,
    data: Dict[str, Any],
    user_id: str
) -> Dict[str, Any]:
    """
    Invoke a Dapr service with user context.
    """
    try:
        payload = json.dumps(data, default=str)  # Handle datetime serialization

        with DaprClient() as dapr:
            response = await dapr.invoke_method(
                app_id=app_id,
                method_name=method_name,
                data=payload,
                metadata={
                    "user_id": str(user_id),
                    "content_type": "application/json",
                    "timestamp": str(int(time.time()))
                }
            )

        # Parse the response
        response_data = {}
        if response.data.getvalue():
            response_str = response.data.getvalue().decode('utf-8')
            if response_str.strip():
                response_data = json.loads(response_str)

        logger.info(f"Service invocation successful: {app_id}.{method_name} for user {user_id}")
        return {
            "success": True,
            "data": response_data,
            "status_code": getattr(response, 'status_code', 200)
        }

    except Exception as e:
        logger.error(f"Service invocation failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "data": None
        }

@app.post("/api/services/invoke")
async def invoke_external_service(request: ServiceCallRequest):
    """Invoke an external service via Dapr."""
    result = await invoke_service_with_context(
        app_id=request.app_id,
        method_name=request.method_name,
        data=request.data,
        user_id=request.user_id
    )

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])

    return result

# Background task example
from celery import Celery

celery_app = Celery("dapr_invoker")

@celery_app.task
def background_invoke_service(app_id: str, method_name: str, data: Dict[str, Any], user_id: str):
    """Background task to invoke services asynchronously."""
    import asyncio

    async def _invoke():
        return await invoke_service_with_context(app_id, method_name, data, user_id)

    return asyncio.run(_invoke())
```

## Error Handling Strategies

### Retry Logic
```python
import asyncio
from functools import wraps

def with_retry(max_attempts=3, delay=1, backoff=2):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    result = await func(*args, **kwargs)
                    # If result indicates success, return it
                    if result and isinstance(result, dict) and result.get("success", True):
                        return result
                    return result
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(delay * (backoff ** attempt))  # Exponential backoff
                    else:
                        logger.error(f"Service invocation failed after {max_attempts} attempts: {str(e)}")

            return {"success": False, "error": str(last_exception)}

        return wrapper
    return decorator

@with_retry(max_attempts=3, delay=1, backoff=2)
async def reliable_invoke_service(app_id: str, method_name: str, data: Dict[str, Any], user_id: str):
    return await invoke_service_with_context(app_id, method_name, data, user_id)
```

### Timeout Configuration
```python
import grpc
from dapr.clients.grpc._request import InvokeMethodRequest
from dapr.proto import common_v1

async def invoke_with_timeout(
    app_id: str,
    method_name: str,
    data: Dict[str, Any],
    user_id: str,
    timeout_seconds: int = 30
):
    """
    Invoke a service with a specific timeout.
    """
    try:
        payload = json.dumps(data)

        with DaprClient() as dapr:
            # Create a context with timeout
            import grpc
            from dapr.conf import Settings
            settings = Settings()

            response = await dapr.invoke_method(
                app_id=app_id,
                method_name=method_name,
                data=payload,
                metadata={"user_id": str(user_id)},
                timeout=timeout_seconds
            )

        response_data = json.loads(response.data.getvalue().decode('utf-8')) if response.data.getvalue() else {}
        return {"success": True, "data": response_data}

    except grpc.aio.AioRpcError as e:
        if e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
            logger.error(f"Service invocation timed out after {timeout_seconds}s")
        else:
            logger.error(f"Service invocation RPC error: {e.details()}")
        return {"success": False, "error": f"RPC error: {e.details()}"}
    except Exception as e:
        logger.error(f"Service invocation failed: {str(e)}")
        return {"success": False, "error": str(e)}
```

## Circuit Breaker Pattern
```python
import time
from enum import Enum
from typing import Callable, Any

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class DaprCircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60, timeout_seconds=30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.timeout_seconds = timeout_seconds
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    def call(self, app_id: str, method_name: str, data: Dict[str, Any], user_id: str):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN - service temporarily unavailable")

        try:
            # Attempt the service call
            result = asyncio.run(self._invoke_service_internal(app_id, method_name, data, user_id))
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise e

    async def _invoke_service_internal(self, app_id: str, method_name: str, data: Dict[str, Any], user_id: str):
        payload = json.dumps(data)

        with DaprClient() as dapr:
            response = await dapr.invoke_method(
                app_id=app_id,
                method_name=method_name,
                data=payload,
                metadata={"user_id": str(user_id)},
                timeout=self.timeout_seconds
            )

        response_data = json.loads(response.data.getvalue().decode('utf-8')) if response.data.getvalue() else {}
        return response_data

    def on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
```