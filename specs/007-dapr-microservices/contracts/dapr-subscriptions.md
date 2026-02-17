# Dapr Subscription Contracts

## GET /dapr/subscribe

Auto-registered by `DaprApp(app)`. Returns subscription list.

**Response** (200):
```json
[
  {
    "pubsubname": "kafka-pubsub",
    "topic": "todo-events",
    "route": "/api/dapr/notifications",
    "metadata": {}
  },
  {
    "pubsubname": "kafka-pubsub",
    "topic": "todo-events",
    "route": "/api/dapr/recurring",
    "metadata": {}
  }
]
```

## POST /api/dapr/notifications

Called by Dapr when events matching notification subscription arrive.

**Request Body** (CloudEvent):
```json
{
  "id": "uuid",
  "source": "todo-backend",
  "type": "com.dapr.event.sent",
  "specversion": "1.0",
  "datacontenttype": "application/json",
  "data": {
    "event_type": "task-created",
    "timestamp": "2026-02-15T10:00:00Z",
    "user_id": 123,
    "payload": {
      "task_id": 1,
      "title": "My task"
    }
  }
}
```

**Response** (200): `{"status": "SUCCESS"}` — event processed
**Response** (200): `{"status": "DROP"}` — event intentionally skipped (missing user_id)
**Response** (500): Dapr retries delivery

## POST /api/dapr/recurring

Called by Dapr when recurring-task-created events arrive.

**Request/Response**: Same CloudEvent format as notifications.

## GET /api/dapr/health

Service invocation endpoint. Callable via Dapr sidecar.

**Via Dapr**: `GET http://localhost:3500/v1.0/invoke/todo-backend/method/api/dapr/health`
**Via CLI**: `dapr invoke --app-id todo-backend --method api/dapr/health --verb GET`

**Response** (200):
```json
{
  "status": "healthy",
  "app_id": "todo-backend",
  "dapr_enabled": true,
  "pubsub_component": "kafka-pubsub",
  "subscriptions_active": 2,
  "events_published": 42,
  "events_received": 38
}
```