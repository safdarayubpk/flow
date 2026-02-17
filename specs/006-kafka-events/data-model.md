# Data Model: Kafka Event-Driven Architecture

**Feature**: 006-kafka-events | **Date**: 2026-02-10

## Overview

This feature does not add new database entities. It defines Kafka event schemas that wrap existing Task data.

## Event Envelope Schema

All events use a common envelope structure:

```python
@dataclass
class TaskEvent:
    """Base event envelope for all task-related events."""
    event_type: str          # e.g., "task-created", "task-updated"
    timestamp: str           # ISO 8601 format, UTC (e.g., "2026-02-10T12:00:00+00:00")
    user_id: int             # User who owns the task (REQUIRED for isolation)
    payload: dict            # Event-specific data
```

### JSON Example

```json
{
  "event_type": "task-created",
  "timestamp": "2026-02-10T12:00:00+00:00",
  "user_id": 123,
  "payload": {
    "task_id": 456,
    "title": "Buy groceries",
    "priority": "high",
    "tags": ["shopping", "urgent"],
    "due_date": "2026-02-15T09:00:00+00:00"
  }
}
```

## Event Type Payloads

### task-created

Published when: `TaskService.create_task()` completes successfully

```python
payload = {
    "task_id": int,           # Primary key of created task
    "title": str,             # Task title
    "priority": Optional[str], # "low", "medium", "high", or None
    "tags": List[str],        # Tag names (may be empty)
    "due_date": Optional[str]  # ISO 8601 or None
}
```

### task-updated

Published when: `TaskService.update_task()` completes successfully

```python
payload = {
    "task_id": int,           # Primary key of updated task
    "changes": dict           # Only the fields that changed
}

# Example changes:
# {"title": "New title", "priority": "high"}
```

### task-completed

Published when: `TaskService.toggle_task_completion()` sets `completed=True`

```python
payload = {
    "task_id": int            # Primary key of completed task
}
```

### task-deleted

Published when: `TaskService.delete_task()` completes (soft delete)

```python
payload = {
    "task_id": int            # Primary key of deleted task
}
```

### reminder-triggered

Published when: Existing reminder scheduler from Phase V.1 fires a reminder

```python
payload = {
    "task_id": int,           # Primary key of task with reminder
    "title": str,             # Task title for notification display
    "due_date": Optional[str]  # When the task is due
}
```

### recurring-task-created

Published when: `TaskService.create_task()` with `recurrence_rule` set

```python
payload = {
    "task_id": int,           # Primary key of recurring task
    "title": str,             # Task title
    "recurrence_rule": str    # Recurrence pattern (e.g., "daily", "weekly")
}
```

### recurring-instance-created

Published when: Recurring Consumer creates a new task instance

```python
payload = {
    "task_id": int,            # Primary key of NEW instance
    "parent_task_id": int,     # Primary key of recurring parent
    "title": str,              # Inherited title
    "scheduled_date": str      # When this instance is scheduled (ISO 8601)
}
```

## Pydantic Models

```python
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class TaskEventBase(BaseModel):
    """Base model for all task events."""
    event_type: str
    timestamp: datetime
    user_id: int
    payload: Dict[str, Any]

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TaskCreatedPayload(BaseModel):
    task_id: int
    title: str
    priority: Optional[str] = None
    tags: List[str] = []
    due_date: Optional[datetime] = None


class TaskUpdatedPayload(BaseModel):
    task_id: int
    changes: Dict[str, Any]


class TaskCompletedPayload(BaseModel):
    task_id: int


class TaskDeletedPayload(BaseModel):
    task_id: int


class ReminderTriggeredPayload(BaseModel):
    task_id: int
    title: str
    due_date: Optional[datetime] = None


class RecurringTaskCreatedPayload(BaseModel):
    task_id: int
    title: str
    recurrence_rule: str


class RecurringInstanceCreatedPayload(BaseModel):
    task_id: int
    parent_task_id: int
    title: str
    scheduled_date: datetime
```

## Validation Rules

1. **user_id**: REQUIRED on every event; consumers MUST validate presence
2. **timestamp**: REQUIRED; UTC timezone; ISO 8601 format
3. **event_type**: REQUIRED; must match one of the 7 defined types
4. **payload.task_id**: REQUIRED on all payloads; must be valid integer

## Topic Configuration

| Setting | Value | Rationale |
|---------|-------|-----------|
| Topic name | `todo-events` | Single topic for all event types |
| Partitions | 1 (default) | Local dev; no parallelism needed |
| Replication | 1 | Single broker |
| Retention | 7 days (default) | Local dev cleanup |

## Consumer Groups

| Consumer | Group ID | Subscribed Events |
|----------|----------|-------------------|
| Notification Consumer | `notification-service` | `task-created`, `reminder-triggered` |
| Recurring Consumer | `recurring-service` | `recurring-task-created` |
