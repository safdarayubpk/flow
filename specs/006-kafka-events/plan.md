# Implementation Plan: Kafka Event-Driven Architecture

**Branch**: `006-kafka-events` | **Date**: 2026-02-10 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-kafka-events/spec.md`

## Summary

Add Kafka-based event publishing and consuming to the existing Todo app from Phase 005-advanced-todo-features. Every task CRUD operation will publish events to Kafka, with two consumers (Notification, Recurring) processing them as FastAPI background tasks. Uses local Docker Compose for Kafka infrastructure with fire-and-forget pattern to ensure zero impact on existing functionality.

## Technical Context

**Language/Version**: Python 3.13+ (backend only; no frontend changes)
**Primary Dependencies**: FastAPI, SQLModel, aiokafka>=0.10.0 (new)
**Storage**: Neon PostgreSQL (existing, no schema changes for Kafka)
**Testing**: pytest with async support for Kafka operations
**Target Platform**: Linux server (local development via Docker)
**Project Type**: Web application (backend extension only)
**Performance Goals**: Events published within 1 second of operation; consumers process within 2-5 seconds
**Constraints**: Fire-and-forget (Kafka failures don't block operations); local-only Kafka; no new API endpoints
**Scale/Scope**: Existing user base; 7 event types; 2 consumers

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Spec-Driven Development | ✅ PASS | Spec complete with 27 FRs, 10 SCs, clarifications resolved |
| II. AI-Only Implementation | ✅ PASS | All code to be generated via SDD workflow |
| III. Iterative Evolution | ✅ PASS | Builds on Phase V.1 (005-advanced-todo-features) |
| IV. Reusability and Modularity | ✅ PASS | Uses kafka-producer-pattern, kafka-consumer-pattern skills |
| V. Security and Isolation | ✅ PASS | user_id in every event; consumers validate isolation |
| VI. Cloud-Native Readiness | ✅ PASS | Event-driven pattern; Docker Compose; externalized config |

**Constitution Gate**: PASSED

## Project Structure

### Documentation (this feature)

```text
specs/006-kafka-events/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output (event schemas)
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (not applicable - no new API)
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
backend/backend/src/
├── services/
│   ├── kafka/                    # NEW: Kafka integration
│   │   ├── __init__.py          # Exports producer and consumer
│   │   ├── producer.py          # KafkaProducer singleton, produce_event()
│   │   ├── consumer.py          # KafkaEventConsumer class
│   │   └── handlers.py          # Event handlers (notification, recurring)
│   ├── task_service.py          # MODIFY: Add event publishing calls
│   └── recurring_service.py     # MODIFY: Publish recurring events
├── main.py                       # MODIFY: Add Kafka lifespan integration
└── core/
    └── config.py                 # MODIFY: Add Kafka env vars

docker-compose.kafka.yml          # NEW: At repository root
```

**Structure Decision**: Backend-only extension. New `services/kafka/` module follows existing service pattern. No frontend changes required.

## Complexity Tracking

> No constitution violations requiring justification.

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| Single topic | `todo-events` for all event types | Simplicity for beginners; routing via event_type field |
| In-process consumers | FastAPI background tasks | No separate deployment; aligns with beginner-friendly constraint |
| Fire-and-forget | Producer doesn't wait/retry | Non-blocking; graceful degradation per FR-013 |

## Architecture Decisions

### AD-001: Event Publishing Integration Points

Events are published from service layer (not API layer) to ensure consistency:

```
TaskService.create_task() → produce_event("task-created", ...)
TaskService.update_task() → produce_event("task-updated", ...)
TaskService.toggle_task_completion() → produce_event("task-completed", ...)
TaskService.delete_task() → produce_event("task-deleted", ...)
RecurringService.process_recurring_tasks() → produce_event("reminder-triggered", ...)
```

**Rationale**: Service layer has access to user_id and complete task data; ensures events are published regardless of entry point (API or AI chat).

### AD-002: Consumer Registration in Lifespan

Both consumers start as background tasks during FastAPI lifespan:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Existing: DB migrations, recurring scheduler
    # NEW: Kafka producer + consumers
    await get_producer()
    notification_task = asyncio.create_task(notification_consumer.consume_loop())
    recurring_task = asyncio.create_task(recurring_consumer.consume_loop())
    yield
    # Cleanup
    await close_producer()
    notification_task.cancel()
    recurring_task.cancel()
```

**Rationale**: Single deployment unit; no external worker processes; aligns with FR-022.

### AD-003: Event Chaining for Recurring Instances

When Recurring Consumer creates a task instance:
1. Insert task into database
2. Publish `recurring-instance-created` event
3. Publish `task-created` event (for Notification Consumer to react)

**Rationale**: Ensures consistent event flow; all new tasks trigger notifications (FR-025).

## Integration Points

### Existing Code Modifications

| File | Change | Risk |
|------|--------|------|
| `main.py` | Add Kafka lifespan hooks | Low - additive |
| `task_service.py` | Add `produce_event()` calls after CRUD | Low - fire-and-forget |
| `recurring_service.py` | Add event publish for reminders | Low - additive |
| `core/config.py` | Add Kafka env vars with defaults | Low - optional vars |

### New Files

| File | Purpose |
|------|---------|
| `services/kafka/__init__.py` | Module exports |
| `services/kafka/producer.py` | Singleton producer, `produce_event()` |
| `services/kafka/consumer.py` | `KafkaEventConsumer` class |
| `services/kafka/handlers.py` | `process_task_created()`, `process_reminder_triggered()`, `process_recurring_task_created()` |
| `docker-compose.kafka.yml` | Zookeeper + Kafka + Kafka UI |

## Testing Strategy

### Unit Tests
- `test_producer.py`: Mock aiokafka, verify event structure, test graceful failures
- `test_handlers.py`: Test each handler with mock events

### Integration Tests
- Start Kafka via Docker Compose
- Produce events, verify consumption
- Test fire-and-forget when Kafka down

### Manual Testing
1. `docker-compose -f docker-compose.kafka.yml up`
2. Start FastAPI: `uvicorn src.main:app --reload`
3. Create task via UI/API
4. Check Kafka UI (localhost:8080) for events
5. Check console logs for consumer output

## Dependencies

### Python Package (add to requirements.txt)
```
aiokafka>=0.10.0
```

### Docker Images (docker-compose.kafka.yml)
```yaml
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
  kafka:
    image: confluentinc/cp-kafka:7.5.0
  kafka-ui:
    image: provectuslabs/kafka-ui:latest
```

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| aiokafka compatibility with Python 3.13 | High | Test early; fallback to kafka-python if needed |
| Consumer offset loss on restart | Medium | Documented limitation; idempotent handlers |
| Kafka startup delay blocks tests | Low | Health check before tests; wait-for-it script |

## Next Steps

1. `/sp.tasks` - Generate task breakdown
2. Implement Docker Compose first (prerequisite for all testing)
3. Implement producer (core infrastructure)
4. Modify task_service.py (enable event publishing)
5. Implement consumers and handlers
6. Integration testing

---

📋 **Architectural decision detected**: Event publishing from service layer (not API layer)
Document reasoning and tradeoffs? Run `/sp.adr event-publishing-integration`
