"""
Dapr event models and constants for the Todo application.

These models and constants are used for Dapr pub/sub event publishing and subscription.
The event types remain the same as in the original Kafka implementation for compatibility.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class TaskCreatedPayload(BaseModel):
    """Payload for task-created events."""
    task_id: int
    title: str
    priority: Optional[str] = None
    tags: List[str] = []
    due_date: Optional[datetime] = None


class TaskUpdatedPayload(BaseModel):
    """Payload for task-updated events."""
    task_id: int
    changes: Dict[str, Any]


class TaskCompletedPayload(BaseModel):
    """Payload for task-completed events."""
    task_id: int


class TaskDeletedPayload(BaseModel):
    """Payload for task-deleted events."""
    task_id: int


class ReminderTriggeredPayload(BaseModel):
    """Payload for reminder-triggered events."""
    task_id: int
    title: str
    due_date: Optional[datetime] = None


class RecurringTaskCreatedPayload(BaseModel):
    """Payload for recurring-task-created events."""
    task_id: int
    title: str
    recurrence_rule: str


class RecurringInstanceCreatedPayload(BaseModel):
    """Payload for recurring-instance-created events."""
    task_id: int
    parent_task_id: int
    title: str
    scheduled_date: datetime


# Event type constants for consistency
class EventTypes:
    """Constants for event type strings."""
    TASK_CREATED = "task-created"
    TASK_UPDATED = "task-updated"
    TASK_COMPLETED = "task-completed"
    TASK_DELETED = "task-deleted"
    REMINDER_TRIGGERED = "reminder-triggered"
    RECURRING_TASK_CREATED = "recurring-task-created"
    RECURRING_INSTANCE_CREATED = "recurring-instance-created"