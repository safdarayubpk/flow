"""
Dapr publisher for event-driven architecture.

Implements the dapr-pubsub-pattern skill with:
- Fire-and-forget event publishing via Dapr pub/sub
- Graceful failure handling (Dapr down → operation still succeeds)
- User isolation (user_id propagated in metadata)
- Structured logging for observability (FR-011)
"""
import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional

from dapr.clients import DaprClient

from src.core.config import settings
from .events import EventTypes

logger = logging.getLogger(__name__)


def publish_event(
    event_type: str,
    event_data: dict[str, Any],
    user_id: Any,
    topic: Optional[str] = None
) -> bool:
    """
    Publish event via Dapr pub/sub with user isolation.

    Implements fire-and-forget pattern - never crashes endpoint.
    Events are delivered via Dapr pub/sub component (backed by Kafka).

    Args:
        event_type: Event name (e.g., "task-created", "task-completed")
        event_data: Event-specific data to be wrapped in envelope
        user_id: Current user's ID (required for isolation, propagated in metadata)
        topic: Kafka topic (default: settings.kafka_topic)

    Returns:
        True if publish initiated successfully, False if failed

    Note:
        This function implements fire-and-forget pattern.
        Failures are logged but do not crash the calling operation.
    """
    # Use configured topic if not specified
    if topic is None:
        topic = settings.kafka_topic

    # Build event envelope matching the original Kafka format for compatibility
    event_envelope = {
        "event_type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id,
        "payload": event_data,
    }

    # Skip immediately if Dapr is disabled (e.g., HF Spaces with no sidecar)
    if not settings.dapr_enabled:
        logger.debug(f"Dapr disabled, skipping event: {event_type}")
        return False

    try:
        # Use Dapr client to publish event to pubsub component
        with DaprClient() as dapr_client:
            # Publish to the kafka-pubsub component with user_id in metadata
            dapr_client.publish_event(
                pubsub_name=settings.dapr_pubsub_name,
                topic_name=topic,
                data=json.dumps(event_envelope),
                publish_metadata={
                    "user_id": str(user_id),
                },
                data_content_type="application/json",
            )
        logger.info(f"Dapr event published: {event_type} for user {user_id} (topic: {topic})")
        logger.debug(f"Dapr event payload: {event_data}")
        return True
    except Exception as e:
        # Fire-and-forget: log error but don't crash
        logger.warning(f"Failed to publish Dapr event {event_type}: {e}")
        return False


def fire_event(
    event_type: str,
    user_id: Any,
    payload: dict[str, Any],
    topic: Optional[str] = None,
) -> None:
    """
    Fire-and-forget event publishing from any context (sync or async).

    Compatibility wrapper that maintains the same interface as the original
    kafka/producer.py fire_event function to minimize service file changes.

    Args:
        event_type: Event type string (e.g., EventTypes.TASK_CREATED)
        user_id: User ID for isolation
        payload: Event payload data
        topic: Topic name (optional, defaults to configured topic)
    """
    # Call the publish_event function synchronously
    # DaprClient is synchronous so no async complexity needed
    success = publish_event(
        event_type=event_type,
        event_data=payload,
        user_id=user_id,
        topic=topic
    )

    if not success:
        logger.warning(f"Failed to publish event {event_type} for user {user_id}")