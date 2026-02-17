# Feature Specification: Dapr Microservices & Pub/Sub

**Feature Branch**: `007-dapr-microservices`
**Created**: 2026-02-15
**Status**: Draft
**Input**: User description: "Phase V.3: Introduce Dapr to existing Todo app for microservices patterns and pub/sub, replacing direct Kafka usage with Dapr pub/sub component while keeping 100% backward compatibility."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Task Events Published via Dapr Pub/Sub (Priority: P1)

As a todo app user, when I create, update, complete, or delete a task, the system publishes the corresponding event through Dapr pub/sub (backed by the existing Kafka broker) instead of direct aiokafka calls, so that the event-driven architecture becomes broker-agnostic and more maintainable.

**Why this priority**: This is the foundational change — replacing the direct aiokafka producer with Dapr pub/sub. Every other story depends on events flowing through Dapr. Without this, the migration has no effect.

**Independent Test**: Can be fully tested by performing a CRUD operation on a task and verifying the event appears in the Kafka topic via Kafka UI (port 8080), confirming it was routed through Dapr's sidecar rather than direct aiokafka.

**Acceptance Scenarios**:

1. **Given** a running Dapr sidecar alongside the FastAPI backend, **When** a user creates a new task via `POST /api/tasks`, **Then** a `task-created` event is published to the `todo-events` topic through Dapr pub/sub with the same payload structure as before, including `user_id` in metadata.
2. **Given** Dapr pub/sub is configured with the `kafka-pubsub` component, **When** any task CRUD operation occurs, **Then** the event envelope (event_type, timestamp, user_id, payload) is identical to the current format so downstream consumers are unaffected.
3. **Given** the Dapr sidecar is temporarily unreachable, **When** a user performs a task operation, **Then** the REST API still succeeds (fire-and-forget), the failure is logged, and no data is lost from the primary database.

---

### User Story 2 - Notification Logic via Dapr Subscription (Priority: P2)

As a todo app user, when a task-related event occurs (task created, reminder triggered), the notification logic is invoked via a Dapr pub/sub subscription endpoint rather than a long-running in-process Kafka consumer loop, so that notifications are triggered reliably and the architecture is more modular.

**Why this priority**: Moves notification processing from a background consumer loop to a Dapr-managed subscription, which is the primary architectural improvement. Depends on P1 events flowing through Dapr.

**Independent Test**: Can be tested by creating a task and confirming the notification handler is called via the Dapr subscription HTTP endpoint (visible in application logs), replacing the old KafkaEventConsumer notification consumer.

**Acceptance Scenarios**:

1. **Given** a Dapr subscription is registered for `task-created` events on the `todo-events` topic, **When** a new task is created, **Then** the notification handler receives the event via an HTTP callback from Dapr and logs the notification (same behavior as the current `process_task_created` handler).
2. **Given** a Dapr subscription is registered for `reminder-triggered` events, **When** a reminder is triggered by the recurring scheduler, **Then** the reminder notification handler is invoked via Dapr subscription.
3. **Given** user A creates a task, **When** the notification subscription receives the event, **Then** the `user_id` in the event metadata matches user A, ensuring user isolation is maintained.

---

### User Story 3 - Recurring Task Processing via Dapr Subscription (Priority: P3)

As a todo app user who has set up recurring tasks, the recurring task instance creation logic is triggered via a Dapr pub/sub subscription rather than a dedicated Kafka consumer, so that the system handles recurring tasks through the same Dapr-managed event infrastructure.

**Why this priority**: Completes the migration of all Kafka consumers to Dapr subscriptions. Lower priority because the background scheduler still provides a safety net for recurring tasks.

**Independent Test**: Can be tested by creating a task with a recurrence rule and confirming the `recurring-task-created` event triggers the Dapr subscription handler, which creates the next instance.

**Acceptance Scenarios**:

1. **Given** a Dapr subscription is registered for `recurring-task-created` events, **When** a task with a recurrence rule is created, **Then** the recurring handler creates the next task instance and publishes both `recurring-instance-created` and `task-created` events via Dapr pub/sub.
2. **Given** a recurring task instance was already created for a given date, **When** the subscription handler receives a duplicate event, **Then** the handler detects the duplicate and skips creation (idempotency preserved).

---

### User Story 4 - Service Invocation via Dapr (Priority: P4)

As a developer, I can use Dapr service invocation to call internal service methods (e.g., triggering notification or recurring logic programmatically) with user context propagation, so that the app demonstrates at least two Dapr building blocks (pub/sub + service invocation).

**Why this priority**: Adds a second Dapr component (service invocation) as required by success criteria. Lower priority because pub/sub handles the primary communication pattern.

**Independent Test**: Can be tested by invoking the notification or health-check service method via Dapr service invocation and verifying the response, with user_id propagated in metadata.

**Acceptance Scenarios**:

1. **Given** the FastAPI app is registered as a Dapr app (e.g., `app-id=todo-backend`), **When** a Dapr service invocation call is made to a health or status endpoint, **Then** the app responds correctly with user context available from metadata.
2. **Given** user_id is included in Dapr service invocation metadata, **When** the target method processes the request, **Then** user isolation is enforced based on the propagated user_id.

---

### User Story 5 - Local Development with `dapr run` (Priority: P5)

As a developer new to Dapr, I can start the entire local development environment (Kafka via Docker Compose + FastAPI via `dapr run`) with simple, documented commands, so that I can develop and test Dapr features without prior Dapr experience.

**Why this priority**: Developer experience story. Important for the target audience (beginners) but not functionally blocking.

**Independent Test**: Can be tested by following the documented steps from a clean environment: start Docker Kafka, run `dapr run`, and verify all task operations work end-to-end.

**Acceptance Scenarios**:

1. **Given** Docker Kafka is running via `docker-compose -f docker-compose.kafka.yml up -d`, **When** the developer runs `dapr run` with the correct app configuration, **Then** the FastAPI backend starts with its Dapr sidecar and all REST API endpoints respond normally.
2. **Given** the local environment is running, **When** a user performs task operations through the existing UI or API, **Then** events flow through Dapr pub/sub, subscriptions fire, and the entire experience is indistinguishable from the previous Kafka-only setup.

---

### Edge Cases

- What happens when the Dapr sidecar crashes mid-request? The REST API must still respond (fire-and-forget for events; primary DB write is unaffected).
- What happens when Kafka is down but Dapr sidecar is running? Dapr should handle the retry/error; the API endpoint must not block or crash.
- What happens when duplicate events are delivered by Dapr? Handlers must remain idempotent (existing idempotency checks in recurring handler must be preserved).
- What happens when a subscription endpoint returns an error? Dapr should retry delivery per its configured retry policy; the handler must not produce side effects on partial failure.
- What happens when user_id is missing from Dapr metadata? The subscription handler must skip the event and log a warning (same behavior as current consumer validation).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST publish all task events (task-created, task-updated, task-completed, task-deleted, reminder-triggered, recurring-task-created, recurring-instance-created) via Dapr pub/sub using the `kafka-pubsub` component. The existing aiokafka producer MUST be fully removed (clean replacement, no fallback to direct Kafka).
- **FR-002**: System MUST maintain the same event envelope format (event_type, timestamp, user_id, payload) so that any external consumers reading from Kafka are unaffected.
- **FR-003**: System MUST use programmatic Dapr subscriptions (via `/dapr/subscribe` endpoint) to register notification event handlers as FastAPI routes, replacing the in-process `notification_consumer` background task.
- **FR-004**: System MUST use programmatic Dapr subscriptions (via `/dapr/subscribe` endpoint) to register recurring task event handlers as FastAPI routes, replacing the in-process `recurring_consumer` background task.
- **FR-005**: System MUST propagate `user_id` in Dapr pub/sub metadata on every published event, and subscription handlers MUST validate user_id presence before processing.
- **FR-006**: System MUST support Dapr service invocation with user context propagation (at least one endpoint accessible via `dapr invoke`).
- **FR-007**: System MUST continue to run the background recurring task scheduler (60-second polling) as-is, since it serves as a complementary mechanism alongside the Dapr subscription.
- **FR-008**: All existing REST API endpoints, UI interactions, AI chat features, and user isolation MUST continue to work identically.
- **FR-009**: System MUST run in Dapr self-hosted mode using `dapr run` with locally configured Dapr components.
- **FR-010**: System MUST gracefully degrade when Dapr sidecar is unavailable — REST API operations must not fail due to event publishing failures.
- **FR-011**: System MUST produce structured INFO-level log entries for every Dapr pub/sub publish and subscription delivery, including event_type, user_id, and status (success/fail). Errors and skipped events (e.g., missing user_id) MUST be logged at WARNING level.

### Key Entities

- **Dapr Pub/Sub Component (kafka-pubsub)**: Bridges Dapr pub/sub API to the existing Kafka broker. Configured as a Dapr component YAML pointing to `localhost:9092`.
- **Dapr Subscription (Programmatic)**: Programmatic subscriptions via a `/dapr/subscribe` endpoint in the FastAPI app that returns the subscription list. Handlers are standard FastAPI routes invoked by Dapr as HTTP callbacks. This keeps subscription logic co-located with handler code for beginner-friendly discoverability.
- **Task Event**: Same structure as Phase V.2 — event_type, timestamp, user_id, payload. Now published via Dapr instead of direct aiokafka.
- **Dapr App Identity (todo-backend)**: The Dapr app-id for the FastAPI backend, used for service invocation and sidecar binding.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 7 event types are published via Dapr pub/sub and visible in Kafka UI with identical payload format to Phase V.2, verified by executing each CRUD operation once and inspecting the resulting events.
- **SC-002**: During a smoke test of 10 task operations (create, update, complete, delete mix), notification subscription endpoints fire for every applicable event with zero missed deliveries, verified via application logs.
- **SC-003**: Creating a task with a recurrence rule triggers the Dapr subscription handler, which creates exactly 1 next instance per event. Sending the same event twice produces no duplicate instance (idempotency verified by DB query).
- **SC-004**: At least 2 Dapr building blocks are used: pub/sub and service invocation.
- **SC-005**: Local environment reaches fully operational state (all endpoints responding, Dapr sidecar healthy) within 60 seconds of running `docker-compose up -d` followed by `dapr run`.
- **SC-006**: After a smoke test of 20 task operations, the count of events in Kafka UI exactly matches the count of DB write operations, with zero orphan or duplicate events.
- **SC-007**: All existing API endpoint tests (or a defined regression checklist of N endpoints) pass without modification after Dapr integration.
- **SC-008**: Every Dapr subscription handler rejects events missing `user_id` in metadata (returns error/skip), verified by sending one test event without user_id and confirming it is logged and discarded.

## Constraints

- Dapr self-hosted mode only (no Kubernetes, no cloud deployment)
- Existing Kafka broker (via docker-compose.kafka.yml) is reused — no new message broker
- Existing Neon PostgreSQL database is reused — no new database
- Single FastAPI process with Dapr sidecar (no full microservices split into separate containers)
- Cloud deployment deferred to Phase V.4
- No UI changes, no AI chat changes, no schema migrations

## Dependencies

- Dapr CLI and runtime installed locally
- Existing Docker Kafka infrastructure (Zookeeper + Kafka broker + Kafka UI)
- Existing Neon PostgreSQL database
- Existing FastAPI backend with aiokafka-based event system (Phase V.2)
- Existing frontend UI and AI chat features

## Assumptions

- Dapr Python SDK supports async operations compatible with FastAPI's event loop
- Dapr pub/sub component for Kafka can connect to the existing broker at `localhost:9092` without Kafka configuration changes
- Dapr subscription endpoints can coexist with existing FastAPI routes without conflicts
- The Dapr sidecar's HTTP port (default 3500) does not conflict with existing services
- The background recurring scheduler (polling) continues to run alongside Dapr subscriptions as a safety net

## Risks & Mitigation

- **Risk 1: Dapr sidecar adds latency to event publishing.** Mitigation: Fire-and-forget pattern ensures API response times are unaffected; measure pub/sub latency in local testing.
- **Risk 2: Dapr subscription delivery semantics differ from direct Kafka consumer.** Mitigation: Preserve idempotency checks in all handlers; test duplicate delivery scenarios.
- **Risk 3: Local development complexity increases (Dapr CLI + Docker Kafka).** Mitigation: Clear step-by-step documentation for the target beginner audience.

## Clarifications

### Session 2026-02-15

- Q: Which Dapr subscription model should be used (programmatic, declarative, or hybrid)? → A: Programmatic — FastAPI exposes `/dapr/subscribe` endpoint returning the subscription list; handlers are FastAPI routes. Keeps subscription logic co-located with handler code for beginner-friendly discoverability.
- Q: Should the migration be a clean replacement or transitional (keep aiokafka as fallback)? → A: Clean replacement — remove aiokafka producer entirely. All events go through Dapr pub/sub only. Dapr still uses the same Kafka broker underneath, so the data path is identical. Fire-and-forget pattern already handles failures gracefully.
- Q: What level of observability should Dapr event publishing and subscription handlers provide? → A: Structured logging — log every publish and subscription delivery with event_type, user_id, and status (success/fail) at INFO level. Errors and skipped events at WARNING level. No tracing or metrics infrastructure needed for this phase.

## Out of Scope

- Full microservices split (separate repos/containers per service)
- Cloud deployment or Kubernetes-based Dapr
- Voice or multi-language features
- New database systems or schema migrations
- Changes to the frontend UI or AI chat functionality
- Dapr state store or secrets management components (beyond pub/sub and service invocation)