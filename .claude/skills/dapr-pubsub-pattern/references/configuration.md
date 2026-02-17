# Dapr Pub/Sub Component Configuration

## Kafka Pub/Sub Component Example

To use this skill, you need to have a Dapr pub/sub component configured. Here's an example configuration for Kafka:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "localhost:9092"
  - name: consumerGroup
    value: "dapr-consumers"
  - name: clientID
    value: "dapr-kafka-client"
  - name: authRequired
    value: "false"
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

class TodoEvent(BaseModel):
    action: str
    task_id: int
    user_id: str
    details: Dict[str, Any] = {}

async def publish_todo_event(topic_name: str, event_data: Dict[str, Any], user_id: str) -> bool:
    """
    Publish an event to Dapr pub/sub with user context.
    """
    try:
        event_json = json.dumps(event_data, default=str)  # Handle datetime serialization

        with DaprClient() as dapr:
            await dapr.publish_event(
                pubsub_name="kafka-pubsub",
                topic_name=topic_name,
                data=event_json,
                metadata={
                    "user_id": str(user_id),
                    "content_type": "application/json",
                    "timestamp": str(int(time.time()))
                }
            )

        logger.info(f"Published event to {topic_name} for user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to publish event: {str(e)}")
        return False

@app.post("/api/tasks/{task_id}/events")
async def create_task_event(task_id: int, event: TodoEvent):
    """Publish a task-related event."""
    success = await publish_todo_event(
        topic_name="todo-events",
        event_data=event.dict(),
        user_id=event.user_id
    )

    if not success:
        raise HTTPException(status_code=500, detail="Failed to publish event")

    return {"message": "Event published successfully"}

# Background task example
from celery import Celery

celery_app = Celery("dapr_publisher")

@celery_app.task
def background_publish_event(topic_name: str, event_data: Dict[str, Any], user_id: str):
    """Background task to publish events asynchronously."""
    import asyncio

    async def _publish():
        return await publish_todo_event(topic_name, event_data, user_id)

    return asyncio.run(_publish())
```

## Error Handling Strategies

### Retry Logic
```python
import asyncio
from functools import wraps

def with_retry(max_attempts=3, delay=1):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(delay * (2 ** attempt))  # Exponential backoff
                    else:
                        logger.error(f"Failed after {max_attempts} attempts: {str(e)}")

            raise last_exception
        return wrapper
    return decorator

@with_retry(max_attempts=3, delay=1)
async def reliable_publish_todo_event(topic_name: str, event_data: Dict[str, Any], user_id: str):
    return await publish_todo_event(topic_name, event_data, user_id)
```

### Circuit Breaker Pattern
```python
import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise e

    def on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
```