# Tasks: Dapr Microservices & Pub/Sub

**Input**: Design documents from `/specs/007-dapr-microservices/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: No automated test tasks included — spec uses manual smoke tests and Kafka UI verification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app (monorepo)**: `backend/` for FastAPI, `backend/components/` for Dapr YAML configs, `backend/backend/src/` for Python source

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install Dapr runtime, create component configs, add Python dependencies.

- [x] T001 Install Dapr CLI and initialize self-hosted runtime via `dapr init`
- [x] T002 [P] Create Dapr kafka-pubsub component YAML in `backend/components/kafka-pubsub.yaml`
- [x] T003 [P] Add `dapr>=1.14.0` and `dapr-ext-fastapi>=1.14.0` to `backend/requirements.txt`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Verify Dapr sidecar works with existing app, create the Dapr integration module with publisher and event types. All user stories depend on this phase.

**CRITICAL**: No user story work can begin until this phase is complete.

- [x] T004 Verify Dapr sidecar starts alongside existing FastAPI app via `dapr run --app-id todo-backend --app-port 8000 --resources-path ./backend/components`
- [x] T005 [P] Create Dapr module init in `backend/backend/src/services/dapr/__init__.py`
- [x] T006 [P] Copy EventTypes constants from `backend/backend/src/services/kafka/events.py` to `backend/backend/src/services/dapr/events.py`
- [x] T007 Create Dapr publisher with `fire_event()` compatibility wrapper in `backend/backend/src/services/dapr/publisher.py`
- [x] T008 Add Dapr configuration settings (DAPR_PUBSUB_NAME, DAPR_APP_ID, DAPR_ENABLED) to `backend/backend/src/core/config.py`

**Checkpoint**: Dapr sidecar running, publisher module ready, EventTypes available — user story implementation can now begin.

---

## Phase 3: User Story 1 — Task Events Published via Dapr Pub/Sub (Priority: P1) MVP

**Goal**: Replace all `fire_event()` calls in task_service.py and recurring_service.py to route through Dapr pub/sub instead of direct aiokafka. All 7 event types flow through Dapr with identical payload format.

**Independent Test**: Perform a CRUD operation on a task and verify the event appears in Kafka UI (port 8080) with the same envelope format as Phase V.2, confirming it was routed through Dapr's sidecar.

### Implementation for User Story 1

- [x] T009 [P] [US1] Update imports in `backend/backend/src/services/task_service.py` to use `from services.dapr.publisher import fire_event` instead of kafka producer
- [x] T010 [P] [US1] Update imports in `backend/backend/src/services/recurring_service.py` to use `from services.dapr.publisher import fire_event` instead of kafka producer
- [x] T011 [US1] Verify all 7 event types publish via Dapr and appear in Kafka UI with correct envelope format (event_type, timestamp, user_id, payload)

**Checkpoint**: All task CRUD events flow through Dapr pub/sub. SC-001 can be partially verified. MVP is functional.

---

## Phase 4: User Story 2 — Notification Logic via Dapr Subscription (Priority: P2)

**Goal**: Replace the in-process `notification_consumer` Kafka consumer loop with a Dapr HTTP subscription handler. Dapr delivers `task-created` and `reminder-triggered` events to a FastAPI endpoint instead of polling Kafka.

**Independent Test**: Create a task and confirm the notification handler is called via the Dapr subscription HTTP endpoint (visible in application logs with structured event_type, user_id, status).

### Implementation for User Story 2

- [x] T012 [US2] Create notification subscription handler (processes `task-created` and `reminder-triggered`) in `backend/backend/src/services/dapr/subscriptions.py`
- [x] T013 [US2] Register DaprApp wrapper and notification subscription (`@dapr_app.subscribe`) in `backend/backend/src/main.py`
- [x] T014 [US2] Remove `notification_consumer` background task from `backend/backend/src/main.py` lifespan
- [x] T015 [US2] Verify notification subscription fires for task-created and reminder-triggered events via application logs

**Checkpoint**: Notification events delivered via Dapr push instead of Kafka consumer poll. SC-002 can be partially verified.

---

## Phase 5: User Story 3 — Recurring Task Processing via Dapr Subscription (Priority: P3)

**Goal**: Replace the in-process `recurring_consumer` Kafka consumer loop with a Dapr HTTP subscription handler for `recurring-task-created` events. Idempotency check preserved. Background scheduler retained as safety net (FR-007).

**Independent Test**: Create a task with a recurrence rule and confirm the `recurring-task-created` event triggers the Dapr subscription handler, which creates exactly one next instance. Duplicate event produces no duplicate instance.

**Depends on**: US2 (DaprApp wrapper and subscriptions.py already exist)

### Implementation for User Story 3

- [x] T016 [US3] Add recurring subscription handler (processes `recurring-task-created` with idempotency check) to `backend/backend/src/services/dapr/subscriptions.py`
- [x] T017 [US3] Register recurring subscription (`@dapr_app.subscribe`) in `backend/backend/src/main.py`
- [x] T018 [US3] Remove `recurring_consumer` background task from `backend/backend/src/main.py` lifespan
- [x] T019 [US3] Verify recurring subscription fires and idempotency check prevents duplicate instance creation

**Checkpoint**: All Kafka consumers replaced by Dapr subscriptions. SC-003 can be partially verified.

---

## Phase 6: User Story 4 — Service Invocation via Dapr (Priority: P4)

**Goal**: Add a Dapr service invocation endpoint (`GET /api/dapr/health`) demonstrating the second Dapr building block. Returns health status with event counters and supports user context propagation via Dapr metadata.

**Independent Test**: Invoke the health endpoint via `dapr invoke --app-id todo-backend --method api/dapr/health --verb GET` and verify the response includes status, app_id, and subscription info.

### Implementation for User Story 4

- [x] T020 [US4] Create service invocation health endpoint in `backend/backend/src/services/dapr/service_invocation.py`
- [x] T021 [US4] Register service invocation router in `backend/backend/src/main.py`
- [x] T022 [US4] Verify service invocation via `dapr invoke` CLI and direct HTTP call to `localhost:3500/v1.0/invoke/todo-backend/method/api/dapr/health`

**Checkpoint**: Two Dapr building blocks operational (pub/sub + service invocation). SC-004 verified.

---

## Phase 7: User Story 5 — Local Development with `dapr run` (Priority: P5)

**Goal**: Validate the complete local development workflow from a clean state. Ensure quickstart.md accurately documents the setup steps and a beginner can follow them successfully.

**Independent Test**: From a clean state, follow the documented steps: start Docker Kafka, run `dapr run`, verify all task operations work end-to-end with events flowing through Dapr.

### Implementation for User Story 5

- [x] T023 [US5] Validate end-to-end local dev workflow per `specs/007-dapr-microservices/quickstart.md` from clean state
- [x] T024 [US5] Update `specs/007-dapr-microservices/quickstart.md` with any corrections discovered during validation

**Checkpoint**: Developer onboarding path validated. SC-005 can be verified.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Remove old aiokafka code, finalize dependencies, run all success criteria smoke tests.

### Cleanup

- [x] T025 [P] Remove entire `backend/backend/src/services/kafka/` directory (producer.py, consumer.py, handlers.py, events.py, __init__.py)
- [x] T026 [P] Remove `aiokafka>=0.10.0` from `backend/requirements.txt` and verify final dependency list
- [x] T027 Remove Kafka producer startup/shutdown from `backend/backend/src/main.py` lifespan
- [x] T028 Remove stale Kafka consumer config settings (KAFKA_NOTIFICATION_GROUP_ID, KAFKA_RECURRING_GROUP_ID) from `backend/backend/src/core/config.py`

### Success Criteria Verification

- [x] T029 Smoke test — all 7 event types published via Dapr with correct envelope format in Kafka UI (SC-001)
- [x] T030 Smoke test — 10 task operations with zero missed notification deliveries in logs (SC-002)
- [x] T031 Smoke test — recurring idempotency: duplicate event produces no duplicate instance in DB (SC-003)
- [x] T032 Smoke test — subscription handlers reject events missing user_id, logged at WARNING (SC-008)
- [x] T033 Regression test — existing API endpoints respond identically to pre-Dapr behavior (SC-007)
- [x] T034 Smoke test — 20 task operations, event count in Kafka UI matches DB write count exactly (SC-006)
- [x] T035 Startup timing — local environment operational within 60 seconds of docker-compose + dapr run (SC-005)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup (T001-T003) — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Foundational (T004-T008)
- **US2 (Phase 4)**: Depends on US1 (events must flow through Dapr before subscriptions can receive them)
- **US3 (Phase 5)**: Depends on US2 (DaprApp wrapper and subscriptions.py created in US2)
- **US4 (Phase 6)**: Depends on Foundational only — can run in parallel with US2/US3 if desired
- **US5 (Phase 7)**: Depends on US1-US4 (validates entire stack end-to-end)
- **Polish (Phase 8)**: Depends on US1-US4 (cleanup after all features work; US5 can overlap)

### User Story Dependencies

- **US1 (P1)**: Depends on Foundational (Phase 2) — no other story dependencies
- **US2 (P2)**: Depends on US1 — needs events flowing through Dapr
- **US3 (P3)**: Depends on US2 — needs DaprApp wrapper and subscriptions.py
- **US4 (P4)**: Depends on Foundational only — independent of US1-US3
- **US5 (P5)**: Depends on US1-US4 — validates complete workflow

### Within Each User Story

- Import/config changes before functional code
- Functional code before verification
- Verification confirms the story works before moving to next priority

### Parallel Opportunities

- **Phase 1**: T002 and T003 can run in parallel (different files: YAML vs requirements.txt)
- **Phase 2**: T005 and T006 can run in parallel (different files: __init__.py vs events.py)
- **Phase 3**: T009 and T010 can run in parallel (different files: task_service.py vs recurring_service.py)
- **Phase 6**: US4 can run in parallel with US2/US3 (independent endpoint, different files)
- **Phase 8**: T025 and T026 can run in parallel (different operations: directory deletion vs requirements edit)

---

## Parallel Example: User Story 1

```bash
# Launch both service file updates in parallel (different files):
Task: "Update imports in backend/backend/src/services/task_service.py"    # T009
Task: "Update imports in backend/backend/src/services/recurring_service.py" # T010

# Then verify sequentially:
Task: "Verify all 7 event types publish via Dapr in Kafka UI"             # T011
```

## Parallel Example: Foundational Phase

```bash
# Launch module creation in parallel (different files):
Task: "Create Dapr module init in backend/backend/src/services/dapr/__init__.py" # T005
Task: "Copy EventTypes to backend/backend/src/services/dapr/events.py"           # T006

# Then create publisher sequentially (depends on both):
Task: "Create Dapr publisher in backend/backend/src/services/dapr/publisher.py"  # T007
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T008) — CRITICAL, blocks all stories
3. Complete Phase 3: User Story 1 (T009-T011)
4. **STOP and VALIDATE**: Create a task, check Kafka UI for Dapr-routed event
5. Events flow through Dapr — MVP achieved

### Incremental Delivery

1. Setup + Foundational → Dapr sidecar running, publisher ready
2. US1 → Events via Dapr → Validate in Kafka UI (MVP!)
3. US2 → Notification subscriptions → Validate in logs
4. US3 → Recurring subscriptions → Validate idempotency
5. US4 → Service invocation → Validate via `dapr invoke`
6. US5 → Local dev workflow validated
7. Polish → Cleanup aiokafka, run all SC smoke tests

### Single-Developer Strategy

Tasks are ordered for sequential execution by one developer:
1. Setup → Foundational → US1 → US2 → US3 → US4 → US5 → Polish
2. Each story checkpoint validates before proceeding
3. Total: 35 tasks across 8 phases

---

## Notes

- [P] tasks = different files, no dependencies on each other
- [Story] label maps task to specific user story for traceability
- No automated tests — spec uses manual smoke tests via curl + Kafka UI + application logs
- Background recurring scheduler (60-second polling) is intentionally retained (FR-007)
- DaprApp wrapper created in US2 is reused by US3 (shared DaprApp instance)
- `fire_event()` compatibility wrapper minimizes service file diffs (only import path changes)
- All success criteria (SC-001 through SC-008) are covered in Phase 8 verification tasks
