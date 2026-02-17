"""
Dapr subscription handlers for the Todo application.

Implements the dapr-pubsub-pattern skill with:
- Single subscription per topic with internal event routing
- User isolation validation (user_id in metadata)
- Structured logging for observability (FR-011)
- Idempotency for recurring tasks (FR-013)

Note: Dapr routes all messages for a given topic to ONE handler endpoint.
We use a single subscription on 'todo-events' and dispatch by event_type internally.
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

from dapr.ext.fastapi import DaprApp
from cloudevents.pydantic import CloudEvent
from sqlmodel import Session, select
from starlette.responses import JSONResponse

from src.core.database import engine
from src.models.task import Task, TaskCreate
from .events import EventTypes
from .publisher import fire_event


# Import TaskService inside functions to avoid circular import
def _get_task_service():
    from src.services.task_service import TaskService
    return TaskService


logger = logging.getLogger(__name__)

# Notification event types handled by this module
_NOTIFICATION_EVENTS = {EventTypes.TASK_CREATED, EventTypes.REMINDER_TRIGGERED}
_RECURRING_EVENTS = {EventTypes.RECURRING_TASK_CREATED}


def register_subscriptions(dapr_app: DaprApp) -> None:
    """
    Register Dapr subscription handlers on the main app's DaprApp instance.

    Uses a single subscription per topic. Dapr delivers all events from
    'todo-events' to one handler, which dispatches by event_type internally.
    """

    @dapr_app.subscribe(pubsub='kafka-pubsub', topic='todo-events', route='/api/dapr/events')
    async def todo_events_handler(cloud_event: CloudEvent) -> JSONResponse:
        """
        Unified handler for all events on the todo-events topic.

        Dispatches to notification or recurring logic based on event_type.
        Returns Dapr-compatible status responses:
        - {"status": "SUCCESS"} — event processed, acknowledge
        - {"status": "DROP"} — event not relevant, don't retry
        - {"status": "RETRY"} — transient error, retry later
        """
        try:
            # cloud_event.data may be a dict (already parsed) or a JSON string
            raw = cloud_event.data
            event_data = json.loads(raw) if isinstance(raw, (str, bytes, bytearray)) else raw
            event_type = event_data.get('event_type')
            user_id = event_data.get('user_id')

            # User isolation validation (SC-008)
            if not user_id:
                logger.warning(
                    "Event handler: missing user_id, dropping event_type=%s",
                    event_type
                )
                return JSONResponse(content={"status": "DROP"})

            logger.info(
                "Event handler received: %s for user %s", event_type, user_id
            )

            # Dispatch to appropriate processor
            if event_type in _NOTIFICATION_EVENTS:
                await _handle_notification(event_type, event_data)
            elif event_type in _RECURRING_EVENTS:
                await _handle_recurring(event_data)
            else:
                # Unknown event type — drop so Dapr doesn't retry
                logger.debug(
                    "Event handler: unhandled event_type %s, dropping", event_type
                )
                return JSONResponse(content={"status": "DROP"})

            logger.info(
                "Event handler processed: %s for user %s", event_type, user_id
            )
            return JSONResponse(content={"status": "SUCCESS"})

        except Exception as e:
            logger.error(
                "Event handler failed: %s", str(e), exc_info=True
            )
            # Return RETRY for transient errors so Dapr can redeliver
            return JSONResponse(content={"status": "RETRY"})

    logger.info("Dapr subscription registered: /api/dapr/events (topic: todo-events)")


# =============================================================================
# Internal dispatchers
# =============================================================================

async def _handle_notification(event_type: str, event_data: Dict[str, Any]) -> None:
    """Dispatch notification events to the appropriate processor."""
    if event_type == EventTypes.TASK_CREATED:
        await _process_task_created(event_data)
    elif event_type == EventTypes.REMINDER_TRIGGERED:
        await _process_reminder_triggered(event_data)


async def _handle_recurring(event_data: Dict[str, Any]) -> None:
    """Dispatch recurring events to the recurring processor."""
    await _process_recurring_task_created(event_data)


# =============================================================================
# Event processing helpers
# =============================================================================

async def _process_task_created(event: Dict[str, Any]) -> None:
    """
    Handle task-created events for notifications.
    Logs a notification message to the server console (FR-010).
    """
    payload = event.get("payload", {})
    title = payload.get("title", "Unknown Task")
    task_id = payload.get("task_id")
    user_id = event.get("user_id")

    logger.info(
        "Notification: Task '%s' (ID: %s) created for user %s",
        title, task_id, user_id
    )


async def _process_reminder_triggered(event: Dict[str, Any]) -> None:
    """
    Handle reminder-triggered events for notifications.
    Logs a reminder notification message to the server console (FR-010).
    """
    payload = event.get("payload", {})
    title = payload.get("title", "Unknown Task")
    task_id = payload.get("task_id")
    due_date = payload.get("due_date")
    user_id = event.get("user_id")

    logger.info(
        "Reminder: Task '%s' (ID: %s) is due%s for user %s",
        title, task_id,
        f" at {due_date}" if due_date else "",
        user_id
    )


async def _process_recurring_task_created(event: Dict[str, Any]) -> None:
    """
    Handle recurring-task-created events.

    Creates the next 1 instance of the recurring task per FR-011.
    Publishes recurring-instance-created event per FR-024.
    Implements idempotency check to prevent duplicate instances (FR-013).
    """
    user_id = event.get("user_id")
    payload = event.get("payload", {})
    task_id = payload.get("task_id")
    title = payload.get("title", "Unknown Task")
    recurrence_rule = payload.get("recurrence_rule")

    if not recurrence_rule:
        logger.warning(
            "process_recurring_task_created: No recurrence_rule for task %s, skipping",
            task_id
        )
        return

    # Calculate next instance date
    next_date = _calculate_next_occurrence(recurrence_rule)

    # Import TaskService here to avoid circular import
    task_service = _get_task_service()

    # Check for existing instance (idempotency per FR-013)
    with Session(engine) as session:
        existing = session.exec(
            select(Task).where(
                Task.user_id == user_id,
                Task.title == title,
                Task.due_date >= next_date - timedelta(hours=1),
                Task.due_date <= next_date + timedelta(hours=1),
                Task.deleted_at.is_(None)
            )
        ).first()

        if existing:
            logger.debug(
                "Recurring instance already exists for task %s, skipping",
                task_id
            )
            return

        # Create new task instance
        new_task = task_service.create_task(
            session=session,
            task_create=TaskCreate(
                title=title,
                description=f"Recurring instance of task {task_id}",
                due_date=next_date,
                recurrence_rule=recurrence_rule,
            ),
            user_id=user_id
        )

        logger.info(
            "Created recurring instance: Task '%s' (ID: %s) for user %s, scheduled for %s",
            title, new_task.id, user_id, next_date.isoformat()
        )

    # Publish recurring-instance-created event (FR-024)
    fire_event(
        event_type=EventTypes.RECURRING_INSTANCE_CREATED,
        user_id=user_id,
        payload={
            "task_id": new_task.id,
            "parent_task_id": task_id,
            "title": title,
            "scheduled_date": next_date.isoformat(),
        }
    )
    # Note: task-created event is already published by TaskService.create_task()


def _calculate_next_occurrence(recurrence_rule: str) -> datetime:
    """
    Calculate the next occurrence date based on recurrence rule.
    Simplified implementation matching recurring_service.py logic.
    """
    now = datetime.utcnow()

    if "DAILY" in recurrence_rule.upper() or "INTERVAL=1" in recurrence_rule.upper():
        return now + timedelta(days=1)
    elif "WEEKLY" in recurrence_rule.upper() or "INTERVAL=7" in recurrence_rule.upper():
        return now + timedelta(weeks=1)
    elif "MONTHLY" in recurrence_rule.upper():
        return now + timedelta(days=30)
    elif "YEARLY" in recurrence_rule.upper():
        return now + timedelta(days=365)
    else:
        return now + timedelta(days=1)
