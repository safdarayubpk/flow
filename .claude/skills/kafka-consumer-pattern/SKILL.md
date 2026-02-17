---
name: kafka-consumer-pattern
description: "Kafka consumer pattern for todo app background services. Use when implementing event consumers, background workers, or async event processing from Kafka. Triggers: kafka consumer, consume events, event listener, background worker, process events, aiokafka consumer, event handler."
---

# Kafka Consumer Pattern

Async Kafka consumer for background services with user isolation validation.

## Consumer Setup

```python
# services/kafka_consumer.py
import os
import json
import logging
import asyncio
from typing import Callable, Awaitable
from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError

logger = logging.getLogger(__name__)

EventHandler = Callable[[dict], Awaitable[None]]

class KafkaEventConsumer:
    """Reusable Kafka consumer for background services."""

    def __init__(
        self,
        topic: str,
        group_id: str,
        handlers: dict[str, EventHandler] | None = None
    ):
        self.topic = topic
        self.group_id = group_id
        self.handlers: dict[str, EventHandler] = handlers or {}
        self._consumer: AIOKafkaConsumer | None = None
        self._running = False

    def register_handler(self, event_type: str, handler: EventHandler):
        """Register handler for specific event type."""
        self.handlers[event_type] = handler

    async def start(self):
        """Initialize and start consumer."""
        bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
        if not bootstrap_servers:
            logger.error("KAFKA_BOOTSTRAP_SERVERS not set")
            return

        self._consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=bootstrap_servers,
            group_id=self.group_id,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            auto_offset_reset="earliest",
            enable_auto_commit=False,
        )

        await self._consumer.start()
        self._running = True
        logger.info(f"Consumer started: {self.group_id} on {self.topic}")

    async def stop(self):
        """Stop consumer gracefully."""
        self._running = False
        if self._consumer:
            await self._consumer.stop()
            logger.info(f"Consumer stopped: {self.group_id}")

    async def consume_loop(self):
        """Main consumption loop. Run as background task."""
        if not self._consumer:
            await self.start()

        try:
            async for msg in self._consumer:
                if not self._running:
                    break

                try:
                    await self._process_message(msg.value)
                    await self._consumer.commit()
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    # Continue consuming, don't crash
        except KafkaError as e:
            logger.error(f"Kafka error: {e}")
        finally:
            await self.stop()

    async def _process_message(self, event: dict):
        """Route event to appropriate handler."""
        event_type = event.get("event_type")
        user_id = event.get("user_id")

        if not event_type or not user_id:
            logger.warning(f"Invalid event schema: {event}")
            return

        handler = self.handlers.get(event_type)
        if handler:
            logger.debug(f"Processing {event_type} for user {user_id}")
            await handler(event)
        else:
            logger.debug(f"No handler for event type: {event_type}")
```

## Event Handlers

```python
# services/event_handlers.py

async def process_task_created(event: dict):
    """Handle task-created events."""
    user_id = event["user_id"]
    payload = event["payload"]
    task_id = payload.get("task_id")
    title = payload.get("title")

    logger.info(f"Task created: {task_id} for user {user_id}")
    # Add your logic: send notification, update cache, etc.

async def process_task_completed(event: dict):
    """Handle task-completed events."""
    user_id = event["user_id"]
    task_id = event["payload"].get("task_id")

    logger.info(f"Task completed: {task_id} for user {user_id}")
    # Add your logic: analytics, achievements, etc.
```

## Background Service Integration

```python
# main.py
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from services.kafka_consumer import KafkaEventConsumer
from services.event_handlers import process_task_created, process_task_completed

# Create consumer instance
task_consumer = KafkaEventConsumer(
    topic="todo-events",
    group_id="notification-service",
    handlers={
        "task-created": process_task_created,
        "task-completed": process_task_completed,
    }
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start consumer as background task
    consumer_task = asyncio.create_task(task_consumer.consume_loop())
    yield
    # Shutdown
    await task_consumer.stop()
    consumer_task.cancel()

app = FastAPI(lifespan=lifespan)
```

## Standalone Worker

```python
# workers/notification_worker.py
import asyncio
from services.kafka_consumer import KafkaEventConsumer
from services.event_handlers import process_task_created

async def main():
    consumer = KafkaEventConsumer(
        topic="todo-events",
        group_id="notification-worker",
    )
    consumer.register_handler("task-created", process_task_created)

    try:
        await consumer.consume_loop()
    except KeyboardInterrupt:
        await consumer.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

## Event Schema

Expected event structure (from kafka-producer-pattern):

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

## User Isolation

Always validate `user_id` before processing:

```python
async def process_with_isolation(event: dict):
    user_id = event.get("user_id")
    if not user_id:
        logger.warning("Event missing user_id, skipping")
        return

    # Only process for valid user
    user = await get_user(user_id)
    if not user:
        logger.warning(f"User {user_id} not found")
        return

    # Safe to process
    await do_work(event, user)
```

## Requirements

```
aiokafka>=0.10.0
```

## Environment

```
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```
