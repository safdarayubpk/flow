# ADR-0006: Consumer to Dapr Subscription Model Shift

> **Scope**: Replacing in-process Kafka consumer loops with Dapr HTTP subscription handlers, covering subscription registration, handler architecture, and event routing.

- **Status:** Accepted
- **Date:** 2026-02-15
- **Feature:** 007-dapr-microservices
- **Context:** Phase V.2 (006-kafka-events, ADR-0003) established Kafka consumers as FastAPI background tasks running continuous `consume_loop()` iterations within the same process. Phase V.3 needs to replace these with Dapr-managed event delivery. The key decisions are: (1) which Dapr subscription model to use (programmatic vs declarative), (2) how to route different event types to different handlers on the same topic, and (3) what to do with the existing background scheduler.

## Decision

We will replace in-process Kafka consumers with **programmatic Dapr subscriptions**:

- **Subscription Model**: Programmatic via `@dapr_app.subscribe()` decorator from `dapr-ext-fastapi`
- **Registration**: `DaprApp(app)` wrapper auto-generates `GET /dapr/subscribe` endpoint
- **Handler Endpoints**:
  - `POST /api/dapr/notifications` — handles `task-created`, `reminder-triggered`
  - `POST /api/dapr/recurring` — handles `recurring-task-created`
- **Event Format**: Handlers receive CloudEvents 1.0 envelope; extract payload from `data` field
- **Event Routing**: Both subscriptions listen to `todo-events` topic; handlers filter by `event_type` in payload
- **User Isolation**: Handlers validate `user_id` presence; skip and log WARNING if missing
- **Idempotency**: Recurring handler preserves DB-level duplicate check before creating instances
- **Background Scheduler**: Retained as-is (60-second polling for recurring tasks) — runs alongside subscriptions as safety net
- **Removed**: `notification_consumer` and `recurring_consumer` background tasks from FastAPI lifespan

## Consequences

### Positive

- Dapr manages event delivery, retry, and dead-lettering — no custom consumer loop code
- Handlers are standard FastAPI routes — testable with regular HTTP clients (curl, pytest)
- Subscription registration is co-located with handler code (decorator pattern) — easy to discover
- No more background task lifecycle management (start/stop/cancel in lifespan)
- Push-based (Dapr pushes to handler) vs pull-based (consumer polls Kafka) — lower latency
- Background scheduler provides redundancy for recurring tasks

### Negative

- Dapr controls delivery timing and retry — less fine-grained control than custom consumer
- Two subscriptions on same topic means Dapr delivers ALL events to BOTH handlers — handlers must filter by event_type
- Handler must return quickly (Dapr has delivery timeout) — long-running processing needs async offload
- Cannot dynamically add/remove subscriptions at runtime (Dapr reads `/dapr/subscribe` once at startup)
- Background scheduler + subscription may both create recurring instances — idempotency check is critical

## Alternatives Considered

**Alternative A: Declarative YAML subscriptions**
- Define subscriptions in a YAML component file (e.g., `subscription.yaml`)
- Why rejected: Separates subscription config from handler code; harder for beginners to trace event flow; clarification session confirmed programmatic approach.

**Alternative B: Streaming subscriptions (Dapr SDK)**
- Use Dapr's streaming subscription API for real-time event consumption
- Why rejected: More complex setup; designed for high-throughput streaming use cases; overkill for 2-3 event handlers.

**Alternative C: Keep Kafka consumers alongside Dapr subscriptions**
- Run both old consumers and new Dapr subscriptions during transition
- Why rejected: Causes duplicate processing; confusing to debug; clean replacement confirmed in clarification.

**Alternative D: Dapr Bindings instead of Pub/Sub**
- Use Dapr input bindings (triggers) instead of pub/sub subscriptions
- Why rejected: Bindings are designed for external system triggers (not inter-service messaging); pub/sub is the correct Dapr building block for event-driven patterns.

## References

- Feature Spec: [specs/007-dapr-microservices/spec.md](../../specs/007-dapr-microservices/spec.md) (FR-003, FR-004, FR-007)
- Implementation Plan: [specs/007-dapr-microservices/plan.md](../../specs/007-dapr-microservices/plan.md) (Phase C: T011-T014)
- Research: [specs/007-dapr-microservices/research.md](../../specs/007-dapr-microservices/research.md) (R2, R3)
- Supersedes: [ADR-0003](./0003-consumer-execution-model.md) (in-process consumer loops fully replaced by Dapr subscriptions)
- Clarification: spec.md Session 2026-02-15, Q1 (programmatic subscriptions confirmed)