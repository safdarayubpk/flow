# Research: Dapr Microservices & Pub/Sub

**Feature**: 007-dapr-microservices
**Date**: 2026-02-15
**Status**: Complete

## R1: Dapr Python SDK Package Selection

**Decision**: Use `dapr` (core SDK) + `dapr-ext-fastapi` (FastAPI extension)

**Rationale**: The `dapr-ext-fastapi` package provides a `DaprApp` wrapper with a `@dapr_app.subscribe()` decorator that handles programmatic subscription registration automatically. This eliminates the need to manually implement the `/dapr/subscribe` endpoint. The core `dapr` package provides `DaprClient` for event publishing and service invocation.

**Alternatives Considered**:
- Manual `/dapr/subscribe` endpoint (more code, error-prone, no decorator convenience)
- `dapr-ext-grpc` (gRPC-based, unnecessary complexity for HTTP pub/sub)

**Packages**:
```
pip install dapr dapr-ext-fastapi
```

## R2: Programmatic Subscription via DaprApp Decorator

**Decision**: Use `@dapr_app.subscribe(pubsub='kafka-pubsub', topic='todo-events')` decorator pattern

**Rationale**: The `DaprApp(app)` wrapper automatically registers a `GET /dapr/subscribe` endpoint that returns the subscription list. Each `@dapr_app.subscribe()` decorated function becomes a POST route that Dapr calls when events arrive. This is the idiomatic FastAPI + Dapr pattern and keeps subscription logic co-located with handler code.

**How it works**:
1. `DaprApp(app)` wraps the FastAPI app
2. `@dapr_app.subscribe(pubsub='kafka-pubsub', topic='todo-events')` registers a subscription
3. On startup, Dapr sidecar calls `GET /dapr/subscribe` to discover subscriptions
4. When events arrive, Dapr POSTs to the handler route with CloudEvents envelope

**Alternatives Considered**:
- Declarative YAML subscriptions (separates config from code, harder for beginners)
- Streaming subscriptions (more complex, not needed for this use case)

## R3: CloudEvents Format

**Decision**: Accept CloudEvents 1.0 envelope; extract payload data from `data` field

**Rationale**: Dapr automatically wraps all pub/sub messages in CloudEvents 1.0 format. Subscription handlers receive a CloudEvents JSON object with standard fields (`id`, `source`, `type`, `specversion`, `data`, `datacontenttype`). The actual event payload is in the `data` field. The `dapr-ext-fastapi` decorator handles parsing automatically when using `Body()`.

**Event structure received by handler**:
```json
{
  "id": "unique-event-id",
  "source": "todo-backend",
  "type": "com.dapr.event.sent",
  "specversion": "1.0",
  "datacontenttype": "application/json",
  "data": {
    "event_type": "task-created",
    "timestamp": "2026-02-15T10:00:00Z",
    "user_id": 123,
    "payload": { "task_id": 1, "title": "My task" }
  }
}
```

## R4: Publishing Events via DaprClient

**Decision**: Use `DaprClient().publish_event()` with `pubsub_name="kafka-pubsub"` as fire-and-forget

**Rationale**: The `DaprClient` is synchronous by default. For async FastAPI, wrap in `asyncio.to_thread()` or use a sync context manager. The publish call is lightweight — Dapr sidecar handles the actual Kafka write asynchronously. Fire-and-forget pattern: catch exceptions, log, and return False on failure.

**Pattern**:
```python
from dapr.clients import DaprClient
import json

def publish_event(topic: str, data: dict, user_id: str) -> bool:
    try:
        with DaprClient() as client:
            client.publish_event(
                pubsub_name="kafka-pubsub",
                topic_name=topic,
                data=json.dumps(data),
                data_content_type="application/json",
                publish_metadata={"user_id": str(user_id)}
            )
        return True
    except Exception as e:
        logger.warning(f"Failed to publish event: {e}")
        return False
```

**Alternatives Considered**:
- Async DaprClient via gRPC (added complexity, not needed for fire-and-forget)
- HTTP calls to Dapr sidecar directly (bypasses SDK, loses type safety)

## R5: Dapr Component Configuration (kafka-pubsub)

**Decision**: Create `components/kafka-pubsub.yaml` pointing to existing Kafka broker at `localhost:9092`

**Rationale**: Dapr components are YAML files loaded from a `--resources-path` directory. The pubsub.kafka component type connects to the existing Kafka broker. No Kafka configuration changes needed.

**Component YAML**:
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
    value: "dapr-todo-backend"
  - name: authRequired
    value: "false"
  - name: maxMessageBytes
    value: "1048576"
```

## R6: Local Development with `dapr run`

**Decision**: Use `dapr run --app-id todo-backend --app-port 8000 --resources-path ./components -- uvicorn backend.src.main:app --host 0.0.0.0 --port 8000`

**Rationale**: `dapr run` starts the Dapr sidecar alongside the app. The `--resources-path` flag points to the components directory. The `--app-port` tells Dapr where to send subscription callbacks. The `--app-id` is the service identity used for service invocation.

**Prerequisites**:
```bash
# One-time: Install Dapr CLI and initialize
curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | /bin/bash
dapr init  # Sets up placement service (can skip Redis/Zipkin if not needed)

# Per session: Start Kafka + Run with Dapr
docker-compose -f docker-compose.kafka.yml up -d
dapr run --app-id todo-backend --app-port 8000 --resources-path ./components -- uvicorn backend.src.main:app --host 0.0.0.0 --port 8000
```

## R7: Service Invocation Pattern

**Decision**: Expose a `/dapr/health` endpoint callable via `dapr invoke --app-id todo-backend --method dapr/health`

**Rationale**: Service invocation is the second required Dapr building block (SC-004). A health/status endpoint is the simplest demonstration that provides real value (operational readiness check). It can also expose event publishing stats. Accessed via Dapr sidecar at `http://localhost:3500/v1.0/invoke/todo-backend/method/dapr/health`.

## R8: Migration Strategy (aiokafka → Dapr)

**Decision**: Clean replacement in 4 steps: (1) Create Dapr publisher module, (2) Swap all `fire_event()` calls to Dapr publisher, (3) Replace KafkaEventConsumer with DaprApp subscriptions, (4) Remove aiokafka code and dependency.

**Rationale**: Clean replacement confirmed in clarification session. Since Dapr pub/sub uses the same Kafka broker underneath, the data path is identical. The event envelope format is preserved. Existing Kafka UI will still show events.

**Files to modify**:
- `backend/backend/src/services/task_service.py` (7 fire_event calls → Dapr publish)
- `backend/backend/src/services/recurring_service.py` (1 fire_event call → Dapr publish)
- `backend/backend/src/main.py` (remove consumer startup, add DaprApp)
- `backend/backend/src/services/kafka/` (entire directory removed after migration)
- `backend/backend/src/core/config.py` (remove Kafka-specific settings, add Dapr settings)