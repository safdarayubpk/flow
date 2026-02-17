# Feature Specification: Kafka Event-Driven Architecture

**Feature Branch**: `006-kafka-events`
**Created**: 2026-02-10
**Status**: Draft
**Input**: User description: "Phase V.2: Kafka – Event-Driven Architecture. Add simple Kafka-based event publishing and consuming to the existing Todo app from Phase 005-advanced-todo-features, without breaking any existing functionality (REST API, UI, AI chat, user isolation)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Task Events Published to Kafka (Priority: P1)

As a system operator, I want every task operation (create, update, complete, delete) to publish a corresponding event to Kafka so that downstream services can react to task changes asynchronously.

**Why this priority**: This is the foundation of the event-driven architecture. Without producing events, consumers have nothing to consume. Enables all downstream use cases.

**Independent Test**: Can be fully tested by performing CRUD operations on tasks and verifying that corresponding JSON events appear in the Kafka topic. Delivers immediate value as the core event infrastructure.

**Acceptance Scenarios**:

1. **Given** a user creates a new task, **When** the task is saved to the database, **Then** a `task-created` event is published to Kafka with the task details and user_id
2. **Given** a user updates an existing task, **When** the update is saved, **Then** a `task-updated` event is published to Kafka with the changed fields
3. **Given** a user marks a task as complete, **When** the task status changes, **Then** a `task-completed` event is published to Kafka
4. **Given** a user deletes a task, **When** the task is removed, **Then** a `task-deleted` event is published to Kafka
5. **Given** Kafka is unavailable, **When** a task operation occurs, **Then** the operation still succeeds (fire-and-forget pattern) and the failure is logged

---

### User Story 2 - Notification Consumer Reacts to Events (Priority: P1)

As a user, I want to receive notifications when important task events occur (e.g., task created, reminder triggered) so that I stay informed about my task activity.

**Why this priority**: Demonstrates the consumer side of the event-driven architecture. Provides visible user value through notifications.

**Independent Test**: Can be fully tested by creating a task and verifying that the notification consumer processes the event and logs a notification message to the server console. Delivers immediate value in demonstrating event consumption.

**Acceptance Scenarios**:

1. **Given** the notification consumer is running, **When** a `task-created` event is received, **Then** a notification is logged to the server console for that user
2. **Given** the notification consumer is running, **When** a `reminder-triggered` event is received, **Then** a reminder notification is logged to the server console
3. **Given** an event is missing user_id, **When** the consumer receives it, **Then** the event is skipped with a warning log (user isolation enforced)

---

### User Story 3 - Recurring Task Consumer Schedules Instances (Priority: P2)

As a user with recurring tasks, I want future instances of my recurring tasks to be automatically scheduled when I create a recurring task so that I don't have to manually create each instance.

**Why this priority**: Demonstrates a more complex consumer use case. Builds on the existing recurring task feature from Phase V.1.

**Independent Test**: Can be fully tested by creating a recurring task and verifying that the consumer creates future task instances based on the recurrence pattern. Delivers value in automation.

**Acceptance Scenarios**:

1. **Given** the recurring consumer is running, **When** a `recurring-task-created` event is received, **Then** the next 1 instance is scheduled according to the recurrence pattern
2. **Given** a recurring task event, **When** the consumer processes it, **Then** the generated instance belongs to the same user_id (isolation preserved)
3. **Given** the recurring consumer creates a new task instance, **When** the instance is saved to the database, **Then** both `recurring-instance-created` and `task-created` events are published

---

### User Story 4 - Local Kafka Development Environment (Priority: P1)

As a developer, I want to run Kafka locally with a simple `docker-compose up` command so that I can develop and test event-driven features without external dependencies.

**Why this priority**: Essential infrastructure for development and testing. Without this, no Kafka features can be developed or tested locally.

**Independent Test**: Can be fully tested by running `docker-compose up` and verifying that Kafka broker and Zookeeper are accessible. Delivers immediate value for development workflow.

**Acceptance Scenarios**:

1. **Given** I have Docker installed, **When** I run `docker-compose up`, **Then** Kafka broker and Zookeeper start successfully
2. **Given** Kafka is running, **When** I use a Kafka client to produce/consume messages, **Then** messages are sent and received correctly
3. **Given** Kafka is running, **When** I start the FastAPI backend, **Then** it connects to Kafka and can produce events

---

### User Story 5 - Backward Compatibility with Existing Features (Priority: P1)

As a user, I want all existing functionality (REST API, UI, AI chat, user isolation) to continue working unchanged so that adding Kafka doesn't break my workflow.

**Why this priority**: Non-negotiable. The system must remain fully functional for existing users while adding new event capabilities.

**Independent Test**: Can be fully tested by running the existing test suite and performing manual testing of all CRUD, AI chat, and authentication features. Delivers confidence in system stability.

**Acceptance Scenarios**:

1. **Given** Kafka is enabled, **When** I perform task CRUD operations via REST API, **Then** all operations complete successfully as before
2. **Given** Kafka is unavailable, **When** I perform task operations, **Then** operations still succeed (graceful degradation)
3. **Given** Kafka is enabled, **When** I use the AI chat to manage tasks, **Then** AI commands work as before
4. **Given** I am logged in, **When** I access tasks, **Then** I only see my own tasks (user isolation preserved)

---

### Edge Cases

- What happens when Kafka broker is down during task operations? → Operations succeed, event publishing fails silently with error logging (fire-and-forget pattern)
- What happens when a consumer crashes while processing an event? → Event remains uncommitted, will be reprocessed on restart (at-least-once delivery)
- How are duplicate events handled by consumers? → Consumers should be idempotent; processing same event twice produces same result
- What happens if user_id is missing from an event? → Event is skipped with a warning log; user isolation is strictly enforced
- What happens when Kafka is not configured (no KAFKA_BOOTSTRAP_SERVERS)? → Application runs normally without event publishing; events are disabled with a warning log
- How are malformed JSON events handled? → Consumer logs error and skips the message; does not crash

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST publish `task-created` events when tasks are created, including task_id, title, priority, and user_id
- **FR-002**: System MUST publish `task-updated` events when tasks are modified, including task_id, changed fields, and user_id
- **FR-003**: System MUST publish `task-completed` events when tasks are marked complete, including task_id and user_id
- **FR-004**: System MUST publish `task-deleted` events when tasks are deleted, including task_id and user_id
- **FR-005**: System MUST publish `reminder-triggered` events when task reminders fire (triggered by the existing reminder scheduler from Phase V.1, not by Kafka consumers), including task_id, title, due_date, and user_id
- **FR-006**: System MUST publish `recurring-task-created` events when recurring tasks are created, including task_id, title, recurrence_rule, and user_id
- **FR-007**: System MUST include user_id in every event payload to maintain strict user isolation
- **FR-008**: System MUST include a timestamp (ISO 8601 format, UTC) in every event
- **FR-009**: System MUST include an event_type field in every event for routing purposes
- **FR-010**: System MUST implement a Notification Consumer that processes `task-created` and `reminder-triggered` events; initial implementation logs to server console, with future extension to trigger browser notifications/in-app toasts (reusing Phase V.1 notification system)
- **FR-011**: System MUST implement a Recurring Consumer that processes `recurring-task-created` events and schedules the next 1 instance only (re-scheduling occurs when that instance is completed)
- **FR-012**: System MUST provide a Docker Compose configuration with Kafka broker and Zookeeper
- **FR-013**: System MUST gracefully handle Kafka unavailability (fire-and-forget pattern; failures logged but don't crash endpoints)
- **FR-014**: System MUST preserve all existing REST API functionality unchanged
- **FR-015**: System MUST preserve all existing UI functionality unchanged
- **FR-016**: System MUST preserve all existing AI chat functionality unchanged
- **FR-017**: System MUST preserve strict user isolation across all operations
- **FR-018**: Consumers MUST validate user_id presence before processing any event
- **FR-019**: Consumers MUST handle malformed events gracefully (log and skip, don't crash)
- **FR-020**: System MUST use the existing Neon database; no new database required
- **FR-021**: System MUST use aiokafka library for async Kafka operations
- **FR-022**: Consumers MUST run as FastAPI background tasks via the application lifespan (not as separate worker scripts)
- **FR-023**: System MUST log Kafka operations at appropriate levels: INFO for successful publish/consume, DEBUG for event payloads, WARNING for failures
- **FR-024**: Recurring Consumer MUST publish `recurring-instance-created` events when scheduling future task instances, including task_id, parent_task_id, title, scheduled_date, and user_id
- **FR-025**: When Recurring Consumer creates a new task instance in the database, it MUST also publish a `task-created` event for that instance (ensures consistent event flow and Notification Consumer reacts to all new tasks)
- **FR-026**: Kafka-related code MUST be placed in `backend/backend/src/services/kafka/` directory with files: `__init__.py`, `producer.py`, `consumer.py`, `handlers.py`
- **FR-027**: Docker Compose file for Kafka MUST be placed at `docker-compose.kafka.yml` in the repository root

### Key Entities

- **Event**: Represents a task-related event with fields: event_type (string), timestamp (ISO 8601 UTC), user_id (integer), payload (object containing event-specific data)
- **KafkaProducer**: Service responsible for publishing events to Kafka topics, following the kafka-producer-pattern skill
- **KafkaConsumer**: Service responsible for consuming events from Kafka topics, following the kafka-consumer-pattern skill
- **NotificationConsumer**: Specialized consumer that reacts to task-created and reminder-triggered events by sending notifications
- **RecurringConsumer**: Specialized consumer that reacts to recurring-task-created events by scheduling future task instances

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every task CRUD operation produces a corresponding Kafka event within 1 second of operation completion
- **SC-002**: At least 3 event types are implemented and demonstrated (task-created, task-completed, reminder-triggered)
- **SC-003**: Notification consumer processes events and logs notifications to server console within 2 seconds of event receipt
- **SC-004**: Recurring consumer schedules future task instances within 5 seconds of receiving a recurring-task-created event
- **SC-005**: `docker-compose up` starts Kafka and Zookeeper within 60 seconds on a typical development machine
- **SC-006**: All existing tests pass after Kafka integration (100% backward compatibility)
- **SC-007**: System operates normally when Kafka is unavailable (graceful degradation)
- **SC-008**: No event contains data from other users (user isolation verified in all events)
- **SC-009**: Consumers recover and continue processing after temporary failures
- **SC-010**: Events are not lost under normal operation (at-least-once delivery guaranteed)

## Assumptions

- Docker and Docker Compose are available on the development machine
- The existing Todo app from Phase 005-advanced-todo-features is functional and deployed
- Python 3.13+ is available for the backend
- aiokafka library is compatible with the existing FastAPI setup
- Local development uses a single Kafka broker (no clustering for this phase)
- Consumer group IDs are unique per consumer type (e.g., notification-service, recurring-service)
- Consumers run as background tasks within the FastAPI application process (single deployment unit); consumer offsets are not persisted across restarts (limitation for local dev - events may be reprocessed after restart)
- Events use a single topic (todo-events) for simplicity in this phase
- Partitioning strategy is default (round-robin or key-based) for this phase

## Constraints

- **No breaking changes**: All existing REST API, UI, AI chat, and user isolation MUST remain functional
- **Local-only Kafka**: This phase uses local Docker-based Kafka only; no cloud Kafka services
- **Fire-and-forget pattern**: Event publishing failures MUST NOT block or fail task operations
- **Single topic**: All events use a single `todo-events` topic for simplicity
- **No new API endpoints**: Kafka integration is internal; no new REST endpoints exposed
- **Beginner-friendly**: Implementation should be simple and well-documented for learning purposes

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `KAFKA_BOOTSTRAP_SERVERS` | No | `localhost:9092` | Kafka broker address; if unset, events are disabled |
| `KAFKA_TOPIC` | No | `todo-events` | Topic name for all task events |
| `KAFKA_NOTIFICATION_GROUP_ID` | No | `notification-service` | Consumer group for Notification Consumer |
| `KAFKA_RECURRING_GROUP_ID` | No | `recurring-service` | Consumer group for Recurring Consumer |

## File Structure

```
backend/backend/src/services/kafka/
├── __init__.py           # Exports producer and consumer
├── producer.py           # KafkaProducer singleton, produce_event function
├── consumer.py           # KafkaEventConsumer class
└── handlers.py           # Event handlers (notification, recurring)

docker-compose.kafka.yml  # At repository root
```

## Technical Notes for Implementation

### Event Schema

All events follow this structure:
```json
{
  "event_type": "task-created",
  "timestamp": "2026-02-10T12:00:00+00:00",
  "user_id": 123,
  "payload": {
    "task_id": 456,
    "title": "Buy groceries",
    "priority": "high"
  }
}
```

### Event Types and Payloads

| Event Type               | Payload Fields                           |
|--------------------------|------------------------------------------|
| `task-created`           | task_id, title, priority, tags, due_date |
| `task-updated`           | task_id, changes (object with changed fields) |
| `task-completed`         | task_id                                  |
| `task-deleted`           | task_id                                  |
| `reminder-triggered`     | task_id, title, due_date                 |
| `recurring-task-created` | task_id, title, recurrence_rule          |
| `recurring-instance-created` | task_id, parent_task_id, title, scheduled_date |

### Skills to Use

- **kafka-producer-pattern**: For implementing event publishing in FastAPI endpoints
- **kafka-consumer-pattern**: For implementing event consumers
- **user-isolation-enforcer**: For ensuring user_id is present in all events
- **fastapi-todo-advanced-endpoints**: For reference on existing endpoint patterns

### Docker Compose Setup

A minimal Docker Compose file (`docker-compose.kafka.yml`) with:
- Zookeeper: `confluentinc/cp-zookeeper:7.5.0`
- Kafka broker: `confluentinc/cp-kafka:7.5.0` (single instance for local development)
- Kafka UI: `provectuslabs/kafka-ui:latest` for event inspection and topic browsing
- Exposed ports: Zookeeper (2181), Kafka (9092), Kafka UI (8080)

## Clarifications

### Session 2026-02-10

- Q: How should consumers (Notification, Recurring) be executed? → A: FastAPI background tasks (consumers run inside the API process via lifespan)
- Q: How should the Notification Consumer deliver notifications? → A: Start with console logging, but eventually trigger browser notifications/in-app toasts as in Phase V.1
- Q: What log levels should be used for Kafka operations? → A: INFO for event publish/consume success, DEBUG for payloads, WARNING for failures
- Q: When is reminder-triggered event published? → A: By the existing reminder scheduler from Phase V.1, not by Kafka consumers
- Q: Should recurring-instance-created event type be added? → A: Yes, published when Recurring Consumer creates a new instance (includes parent_task_id)
- Q: Are consumer offsets persisted across restarts? → A: No, limitation for local dev; events may be reprocessed after restart
- Q: Should Docker Compose include Kafka UI for debugging? → A: Yes, include Kafka UI (provectuslabs/kafka-ui)
- Q: How many future instances should Recurring Consumer schedule? → A: Next 1 instance only (simplest approach; re-schedule after completion)
- Q: When Recurring Consumer creates a task instance, should it publish task-created event? → A: Yes, ensures consistent event flow and Notification Consumer reacts to all new tasks
- Q: Where should Kafka-related files be placed? → A: `backend/backend/src/services/kafka/` with producer.py, consumer.py, handlers.py

## Out of Scope

- Cloud Kafka deployment (Confluent Cloud, AWS MSK, etc.) - saved for V.4
- Complex partitioning strategies
- Event replay/sourcing
- Dead letter queues
- Schema registry
- Dapr integration - saved for V.3
- Multi-broker Kafka cluster
- Voice commands, multi-language features
