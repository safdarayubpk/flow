# Tasks: Kafka Event-Driven Architecture

**Input**: Design documents from `/specs/006-kafka-events/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, quickstart.md ✓

**Tests**: Tests are included for verification of fire-and-forget pattern and backward compatibility (per SC-006, SC-007).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**Skills to Apply**: `kafka-producer-pattern`, `kafka-consumer-pattern`, `user-isolation-enforcer`, `fastapi-jwt-user-context`

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/backend/src/` (existing FastAPI application)
- **Kafka module**: `backend/backend/src/services/kafka/` (new)
- **Docker**: `docker-compose.kafka.yml` at repository root

---

## Phase 1: Setup (Local Kafka Infrastructure)

**Purpose**: Establish local Kafka development environment (US4 prerequisite for all other stories)

- [x] T001 Create docker-compose.kafka.yml at repository root with Zookeeper, Kafka broker, and Kafka UI
- [x] T002 Add aiokafka>=0.10.0 to backend/requirements.txt
- [x] T003 [P] Add Kafka environment variables to backend/backend/src/core/config.py (KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC, consumer group IDs with defaults)
- [x] T004 Create backend/backend/src/services/kafka/__init__.py with module exports

**Verification**: Run `docker-compose -f docker-compose.kafka.yml up -d` and confirm Kafka UI accessible at localhost:8080

---

## Phase 2: Foundational (Kafka Producer Infrastructure)

**Purpose**: Core producer infrastructure that ALL event publishing depends on

**⚠️ CRITICAL**: No event publishing (US1) can begin until this phase is complete

- [x] T005 Create backend/backend/src/services/kafka/producer.py with singleton pattern using kafka-producer-pattern skill
- [x] T006 Implement get_producer() function that returns None if KAFKA_BOOTSTRAP_SERVERS not set
- [x] T007 Implement close_producer() function for graceful shutdown
- [x] T008 Implement produce_event(event_type, user_id, payload, topic) helper with fire-and-forget pattern
- [x] T009 Add Kafka producer lifespan hooks to backend/backend/src/main.py (initialize on startup, cleanup on shutdown)

**Checkpoint**: Producer ready - run FastAPI, create task via API, check logs for "Kafka producer started" or "events disabled" warning

---

## Phase 3: User Story 4 - Local Kafka Development Environment (Priority: P1) 🎯 MVP

**Goal**: Developer can run `docker-compose up` to start Kafka and see events in Kafka UI

**Independent Test**: Start Kafka via Docker Compose, start FastAPI, verify connection logs appear

### Implementation for User Story 4

- [x] T010 [US4] Verify docker-compose.kafka.yml starts all 3 services (zookeeper, kafka, kafka-ui) within 60 seconds
- [x] T011 [US4] Verify Kafka broker accessible at localhost:9092 from host machine
- [x] T012 [US4] Verify Kafka UI accessible at localhost:8080 and shows topic list
- [x] T013 [US4] Document Kafka startup in specs/006-kafka-events/quickstart.md with troubleshooting steps

**Checkpoint**: US4 complete - `docker-compose -f docker-compose.kafka.yml up` works reliably

---

## Phase 4: User Story 1 - Task Events Published to Kafka (Priority: P1) 🎯 MVP

**Goal**: Every task CRUD operation publishes a corresponding event to Kafka with user_id

**Independent Test**: Create/update/complete/delete task via API, observe events in Kafka UI topic viewer

### Implementation for User Story 1

- [x] T014 [P] [US1] Create Pydantic event models in backend/backend/src/services/kafka/events.py (TaskCreatedPayload, TaskUpdatedPayload, TaskCompletedPayload, TaskDeletedPayload, ReminderTriggeredPayload, RecurringTaskCreatedPayload, RecurringInstanceCreatedPayload)
- [x] T015 [US1] Modify backend/backend/src/services/task_service.py: Add produce_event() call in create_task() for task-created event
- [x] T016 [US1] Modify backend/backend/src/services/task_service.py: Add produce_event() call in update_task() for task-updated event
- [x] T017 [US1] Modify backend/backend/src/services/task_service.py: Add produce_event() call in toggle_task_completion() for task-completed event (only when completed=True)
- [x] T018 [US1] Modify backend/backend/src/services/task_service.py: Add produce_event() call in delete_task() for task-deleted event
- [x] T019 [US1] Modify backend/backend/src/services/task_service.py: Add produce_event() call in create_task() for recurring-task-created event (when recurrence_rule is set)
- [x] T020 [US1] Modify backend/backend/src/services/recurring_service.py: Add produce_event() call for reminder-triggered event when reminder fires
- [x] T021 [US1] Add INFO logging for successful event publishing (in produce_event)
- [x] T022 [US1] Add WARNING logging when Kafka unavailable (fire-and-forget failure handling)

**Checkpoint**: US1 complete - All CRUD operations publish events visible in Kafka UI; operations succeed even when Kafka is down

---

## Phase 5: User Story 5 - Backward Compatibility (Priority: P1) 🎯 MVP

**Goal**: All existing functionality (REST API, UI, AI chat, user isolation) continues working unchanged

**Independent Test**: Run existing test suite; manually test all CRUD operations without Kafka running

### Implementation for User Story 5

- [x] T023 [US5] Verify fire-and-forget: Stop Kafka, perform task CRUD via API, confirm all operations succeed with warning logs
- [x] T024 [US5] Verify REST API: Run backend/backend/test_advanced_features.py and confirm all tests pass
- [x] T025 [US5] Verify user isolation: Confirm user_id is included in every published event payload
- [x] T026 [US5] Verify graceful degradation: Start FastAPI without KAFKA_BOOTSTRAP_SERVERS set, confirm app starts with "events disabled" warning

**Checkpoint**: US5 complete - All existing tests pass (SC-006); system works normally when Kafka unavailable (SC-007)

---

## Phase 6: User Story 2 - Notification Consumer Reacts to Events (Priority: P1)

**Goal**: Notification Consumer processes task-created and reminder-triggered events, logging notifications to server console

**Independent Test**: Create task via API, observe notification log message in FastAPI console within 2 seconds

### Implementation for User Story 2

- [x] T027 [P] [US2] Create backend/backend/src/services/kafka/consumer.py with KafkaEventConsumer class using kafka-consumer-pattern skill
- [x] T028 [P] [US2] Create backend/backend/src/services/kafka/handlers.py with empty handler functions (process_task_created, process_reminder_triggered, process_recurring_task_created)
- [x] T029 [US2] Implement process_task_created handler: Log "🔔 Notification: Task '{title}' created for user {user_id}" to console
- [x] T030 [US2] Implement process_reminder_triggered handler: Log "⏰ Reminder: Task '{title}' is due for user {user_id}" to console
- [x] T031 [US2] Add user_id validation in handlers: Skip event with warning if user_id missing (user-isolation-enforcer skill)
- [x] T032 [US2] Add malformed event handling: Log error and skip if event cannot be parsed
- [x] T033 [US2] Create notification_consumer instance in backend/backend/src/services/kafka/__init__.py with group_id="notification-service"
- [x] T034 [US2] Register notification_consumer in main.py lifespan: Start consume_loop as asyncio.create_task on startup, cancel on shutdown

**Checkpoint**: US2 complete - Create task, see notification log in console within 2 seconds (SC-003)

---

## Phase 7: User Story 3 - Recurring Task Consumer Schedules Instances (Priority: P2)

**Goal**: Recurring Consumer processes recurring-task-created events and schedules the next 1 instance

**Independent Test**: Create recurring task via API, observe new task instance created in database within 5 seconds

**Depends On**: US2 (consumer infrastructure), US1 (event publishing)

### Implementation for User Story 3

- [x] T035 [US3] Implement process_recurring_task_created handler in backend/backend/src/services/kafka/handlers.py
- [x] T036 [US3] In handler: Calculate next instance date based on recurrence_rule (daily, weekly, monthly)
- [x] T037 [US3] In handler: Create new task instance in database with same user_id, title, and scheduled_date
- [x] T038 [US3] In handler: Publish recurring-instance-created event for the new instance
- [x] T039 [US3] In handler: Publish task-created event for the new instance (triggers notification consumer per FR-025)
- [x] T040 [US3] Add idempotency check: Query database for existing instance before creating (avoid duplicates on reprocessing)
- [x] T041 [US3] Create recurring_consumer instance in backend/backend/src/services/kafka/__init__.py with group_id="recurring-service"
- [x] T042 [US3] Register recurring_consumer in main.py lifespan: Start consume_loop as asyncio.create_task on startup, cancel on shutdown

**Checkpoint**: US3 complete - Create recurring task, new instance appears in database within 5 seconds (SC-004)

---

## Phase 8: Polish & Integration Verification

**Purpose**: End-to-end validation and documentation

- [x] T043 [P] Update backend/backend/src/services/kafka/__init__.py exports: producer functions, consumer instances, event models
- [x] T044 [P] Add DEBUG logging for event payloads in produce_event and consume handlers
- [x] T045 Create backend/backend/tests/test_kafka_producer.py: Unit tests mocking aiokafka for event structure and fire-and-forget
- [x] T046 Create backend/backend/tests/test_kafka_handlers.py: Unit tests for each handler with mock events
- [x] T047 Run end-to-end test: Start Kafka, start FastAPI, create task, verify event in Kafka UI, verify notification log
- [x] T048 Run graceful degradation test: Stop Kafka mid-operation, verify operation succeeds with warning log
- [x] T049 Update specs/006-kafka-events/quickstart.md with complete testing instructions
- [x] T050 Verify all SC criteria: SC-001 through SC-010 pass

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion - BLOCKS all user stories
- **US4 (Phase 3)**: Depends on Phase 1 only (Docker Compose verification)
- **US1 (Phase 4)**: Depends on Phase 2 (producer infrastructure)
- **US5 (Phase 5)**: Depends on Phase 4 (needs events to verify backward compat)
- **US2 (Phase 6)**: Depends on Phase 2 (consumer infrastructure)
- **US3 (Phase 7)**: Depends on Phase 6 (uses consumer pattern from US2)
- **Polish (Phase 8)**: Depends on all user stories complete

### User Story Dependencies

- **User Story 4 (P1)**: Infrastructure only - no code dependencies
- **User Story 1 (P1)**: Depends on producer infrastructure (Phase 2)
- **User Story 5 (P1)**: Depends on US1 (verifies backward compat with events)
- **User Story 2 (P1)**: Can start after Phase 2 - Independent of US1
- **User Story 3 (P2)**: Depends on consumer infrastructure (US2 pattern)

### Within Each User Story

- Models/types before service modifications
- Producer modifications before consumer tasks
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- T003 can run parallel with T001, T002
- T014 (event models) can run parallel with T027, T028 (consumer classes)
- All [P] marked tasks within a phase can run in parallel

---

## Parallel Example: User Story 1 + User Story 2

```bash
# After Phase 2 (Foundational) is complete:

# Team Member A - User Story 1 (Publishing):
Task: "Create Pydantic event models in backend/backend/src/services/kafka/events.py"
Task: "Modify task_service.py: Add produce_event() calls for CRUD operations"

# Team Member B - User Story 2 (Consuming):
Task: "Create consumer.py with KafkaEventConsumer class"
Task: "Create handlers.py with notification handler functions"
```

---

## Implementation Strategy

### MVP First (User Stories 1, 4, 5)

1. Complete Phase 1: Setup (Docker Compose)
2. Complete Phase 2: Foundational (Producer)
3. Complete Phase 3: US4 (Verify Kafka works)
4. Complete Phase 4: US1 (Event publishing)
5. Complete Phase 5: US5 (Backward compatibility)
6. **STOP and VALIDATE**: All events publish, all existing tests pass, fire-and-forget works
7. Deploy/demo MVP

### Full Implementation

8. Complete Phase 6: US2 (Notification consumer)
9. Complete Phase 7: US3 (Recurring consumer)
10. Complete Phase 8: Polish & Integration

### Key Success Criteria Mapping

| SC | Task(s) | Verification |
|----|---------|--------------|
| SC-001 | T015-T022 | Event published within 1 second |
| SC-002 | T014-T020 | 3+ event types implemented |
| SC-003 | T029-T034 | Notification logged within 2 seconds |
| SC-004 | T035-T042 | Instance created within 5 seconds |
| SC-005 | T010 | Kafka starts within 60 seconds |
| SC-006 | T024 | All existing tests pass |
| SC-007 | T023, T026 | System works without Kafka |
| SC-008 | T025, T031 | user_id in all events |
| SC-009 | T032 | Consumers recover from failures |
| SC-010 | T008, T047 | Events not lost under normal operation |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Apply kafka-producer-pattern skill for T005-T008
- Apply kafka-consumer-pattern skill for T027-T034
- Apply user-isolation-enforcer skill for T025, T031
