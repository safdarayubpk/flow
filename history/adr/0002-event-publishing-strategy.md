# ADR-0002: Event Publishing Strategy

> **Scope**: Event publishing approach covering integration points, delivery guarantees, and topic structure.

- **Status:** Accepted
- **Date:** 2026-02-10
- **Feature:** 006-kafka-events
- **Context:** Task CRUD operations need to publish events to Kafka for downstream consumers. The decision involves where in the code to publish events, what delivery guarantees to provide, and how to structure topics.

## Decision

We will adopt the following event publishing strategy:

- **Integration Point**: Service layer (TaskService, RecurringService) - not API layer
- **Delivery Pattern**: Fire-and-forget with graceful failure handling
- **Topic Structure**: Single `todo-events` topic; routing via `event_type` field
- **Event Trigger Points**:
  - `TaskService.create_task()` → `task-created`
  - `TaskService.update_task()` → `task-updated`
  - `TaskService.toggle_task_completion()` → `task-completed`
  - `TaskService.delete_task()` → `task-deleted`
  - `RecurringService.process_recurring_tasks()` → `reminder-triggered`
- **Producer Pattern**: Singleton via `get_producer()`, async `produce_event()` helper

## Consequences

### Positive

- Service layer has complete context (user_id, full task data)
- Events fire regardless of entry point (API or AI chat interface)
- Fire-and-forget ensures CRUD operations are never blocked by Kafka
- Application continues working if Kafka is down (graceful degradation)
- Single topic simplifies infrastructure and debugging

### Negative

- No delivery guarantees (events may be lost if Kafka unavailable)
- No ordering guarantees across different event types
- Service layer now has Kafka dependency (increased coupling)
- Single topic doesn't scale for high-throughput scenarios

## Alternatives Considered

**Alternative A: API Layer Publishing**
- Publish events in API route handlers instead of services
- Why rejected: Misses events from AI chat interface; duplicates user_id handling logic

**Alternative B: Transactional Outbox Pattern**
- Store events in database first, relay to Kafka via separate process
- Why rejected: Guarantees delivery but adds significant complexity; out of scope for beginner-friendly phase

**Alternative C: Sync Publishing with Retry**
- Wait for Kafka acknowledgment; retry on failure
- Why rejected: Blocks CRUD operations; violates fire-and-forget requirement from spec

**Alternative D: Multiple Topics per Event Type**
- Separate topics: `task-created`, `task-updated`, etc.
- Why rejected: Adds infrastructure complexity; harder to debug; single topic sufficient for local dev

## References

- Feature Spec: [specs/006-kafka-events/spec.md](../../specs/006-kafka-events/spec.md)
- Implementation Plan: [specs/006-kafka-events/plan.md](../../specs/006-kafka-events/plan.md) (AD-001)
- Related ADRs: [ADR-0001](./0001-kafka-infrastructure-stack.md) (infrastructure dependency)
- Evaluator Evidence: Research item R-003 in research.md
