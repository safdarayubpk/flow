---
name: kafka-producer-pattern
description: "Kafka producer pattern for FastAPI todo app events with user isolation. Use when implementing event publishing to Kafka from FastAPI endpoints. Triggers: kafka producer, publish event, event streaming, task events, audit events, produce to kafka, aiokafka producer."
---

# Kafka Producer Pattern

Async Kafka producer for FastAPI with mandatory user isolation.

## Setup

```python
# services/kafka_producer.py
import os
import json
import logging
from datetime import datetime, timezone
from typing import Any
from aiokafka import AIOKafkaProducer

logger = logging.getLogger(__name__)

_producer: AIOKafkaProducer | None = None

async def get_producer() -> AIOKafkaProducer | None:
    """Get or create singleton producer. Returns None if Kafka unavailable."""
    global _producer
    if _producer is not None:
        return _producer

    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
    if not bootstrap_servers:
        logger.warning("KAFKA_BOOTSTRAP_SERVERS not set, events disabled")
        return None

    try:
        _producer = AIOKafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        await _producer.start()
        logger.info("Kafka producer started")
        return _producer
    except Exception as e:
        logger.error(f"Failed to start Kafka producer: {e}")
        return None

async def close_producer():
    """Shutdown producer gracefully."""
    global _producer
    if _producer:
        await _producer.stop()
        _producer = None
```

## Event Producer Function

```python
# services/kafka_producer.py (continued)

async def produce_event(
    event_type: str,
    user_id: int,
    payload: dict[str, Any],
    topic: str = "todo-events"
) -> bool:
    """
    Produce event with user isolation. Never crashes endpoint.

    Args:
        event_type: Event name (e.g., "task-created", "task-completed")
        user_id: Current user's ID (required for isolation)
        payload: Event-specific data
        topic: Kafka topic (default: todo-events)

    Returns:
        True if sent, False if failed/disabled
    """
    producer = await get_producer()
    if not producer:
        return False

    event = {
        "event_type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id,
        "payload": payload,
    }

    try:
        await producer.send_and_wait(topic, event)
        logger.debug(f"Event produced: {event_type} for user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to produce event: {e}")
        return False
```

## Endpoint Usage

```python
from services.kafka_producer import produce_event

@router.post("/tasks", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user)
):
    # Create task in database
    task = await task_service.create(task_data, current_user.id)

    # Produce event (fire-and-forget, won't crash if Kafka down)
    await produce_event(
        event_type="task-created",
        user_id=current_user.id,
        payload={"task_id": task.id, "title": task.title}
    )

    return task
```

## Lifespan Integration

```python
# main.py
from contextlib import asynccontextmanager
from services.kafka_producer import get_producer, close_producer

@asynccontextmanager
async def lifespan(app: FastAPI):
    await get_producer()  # Initialize on startup
    yield
    await close_producer()  # Cleanup on shutdown

app = FastAPI(lifespan=lifespan)
```

## Event Schema

All events follow this structure:

```json
{
  "event_type": "task-created",
  "timestamp": "2026-02-09T12:00:00+00:00",
  "user_id": 123,
  "payload": {
    "task_id": 456,
    "title": "Buy groceries"
  }
}
```

## Common Event Types

| Event | Payload |
|-------|---------|
| `task-created` | `{task_id, title, priority?}` |
| `task-completed` | `{task_id}` |
| `task-deleted` | `{task_id}` |
| `task-updated` | `{task_id, changes: {...}}` |

## Requirements

```
aiokafka>=0.10.0
```

## Environment

```
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```
