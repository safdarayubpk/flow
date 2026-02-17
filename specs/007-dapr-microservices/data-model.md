# Data Model: Dapr Microservices & Pub/Sub

**Feature**: 007-dapr-microservices
**Date**: 2026-02-15

## Overview

No database schema changes are required. This feature modifies the event transport layer (aiokafka → Dapr pub/sub) without changing the data model. All existing entities (Task, User, Tag, Conversation, Message) remain unchanged.

## Event Entities (Transport Layer)

### Task Event Envelope (unchanged format)

The event payload published via Dapr pub/sub maintains the same structure as Phase V.2:

```
TaskEvent
├── event_type: str          # e.g., "task-created", "task-updated"
├── timestamp: str           # ISO 8601 UTC
├── user_id: int             # Required — user isolation key
└── payload: dict            # Event-specific data
    ├── task_id: int
    ├── title: str (optional, on create)
    ├── changes: dict (optional, on update)
    ├── priority: str (optional)
    ├── tags: list[str] (optional)
    ├── due_date: str (optional)
    ├── recurrence_rule: str (optional)
    └── scheduled_date: str (optional, on recurring-instance-created)
```

### CloudEvents Wrapper (new — added by Dapr)

Dapr automatically wraps events in CloudEvents 1.0 envelope:

```
CloudEvent
├── id: str                  # Unique event ID (Dapr-generated)
├── source: str              # "todo-backend" (from app-id)
├── type: str                # "com.dapr.event.sent"
├── specversion: str         # "1.0"
├── datacontenttype: str     # "application/json"
└── data: TaskEvent          # The actual event payload (unchanged format)
```

### Dapr Pub/Sub Metadata

```
DaprMetadata
├── user_id: str             # Propagated for user isolation
└── content_type: str        # "application/json"
```

## Event Types (unchanged from Phase V.2)

| Event Type | Publisher | Trigger |
|---|---|---|
| `task-created` | TaskService.create_task() | Task creation |
| `task-updated` | TaskService.update_task() | Task field update |
| `task-completed` | TaskService.toggle_task_completion() | Task completion toggle |
| `task-deleted` | TaskService.delete_task() | Task deletion |
| `reminder-triggered` | RecurringService.process_recurring_tasks() | Reminder due |
| `recurring-task-created` | TaskService.create_task() | Task with recurrence_rule |
| `recurring-instance-created` | Subscription handler | Recurring instance created |

## Subscription Routing (new)

| Subscription | Topic | Event Filter | Handler |
|---|---|---|---|
| Notification | `todo-events` | `task-created`, `reminder-triggered` | `/api/dapr/notifications` |
| Recurring | `todo-events` | `recurring-task-created` | `/api/dapr/recurring` |

## State Transitions

No state machine changes. Task lifecycle remains:
```
Created → Updated* → Completed/Deleted
            ↑ Recurring instances created via subscription
```

The only change is the transport mechanism (Dapr pub/sub instead of direct aiokafka).