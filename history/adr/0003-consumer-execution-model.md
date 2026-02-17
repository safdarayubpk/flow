# ADR-0003: Consumer Execution Model

> **Scope**: How Kafka consumers are executed, registered, and managed within the application lifecycle.

- **Status:** Accepted
- **Date:** 2026-02-10
- **Feature:** 006-kafka-events
- **Context:** The application needs two Kafka consumers (Notification Consumer, Recurring Consumer) that process events continuously. The decision involves how these consumers are deployed, started, and integrated with FastAPI.

## Decision

We will run Kafka consumers as FastAPI background tasks within the same process:

- **Execution Model**: In-process asyncio tasks via FastAPI lifespan
- **Registration**: Consumers start during app startup; cancel on shutdown
- **Consumer Implementation**:
  - `notification_consumer`: Processes `task-created`, `reminder-triggered`
  - `recurring_consumer`: Processes `recurring-task-created`
- **Lifecycle Pattern**:
  ```python
  @asynccontextmanager
  async def lifespan(app: FastAPI):
      await get_producer()
      notification_task = asyncio.create_task(notification_consumer.consume_loop())
      recurring_task = asyncio.create_task(recurring_consumer.consume_loop())
      yield
      notification_task.cancel()
      recurring_task.cancel()
      await close_producer()
  ```
- **Consumer Groups**: `notification-service`, `recurring-service`
- **Offset Handling**: Not persisted across restarts (documented limitation)
- **Idempotency**: Check database before creating records; logging is inherently idempotent

## Consequences

### Positive

- Single deployment unit (no separate worker processes to manage)
- Beginner-friendly: `docker-compose up` starts everything
- Consumers share database connections and config with main app
- Easy debugging (all logs in one place)
- Follows existing pattern from recurring task scheduler

### Negative

- Consumers compete with HTTP requests for CPU/memory
- No horizontal scaling of consumers independent of API
- Consumer crash affects the entire application
- Offset loss on restart means potential duplicate processing
- Not production-grade (separate workers preferred for scale)

## Alternatives Considered

**Alternative A: Separate Worker Scripts**
- Run consumers as independent Python scripts/containers
- Why rejected: Adds deployment complexity; multiple processes to monitor; not beginner-friendly

**Alternative B: Celery Task Queue**
- Use Celery workers to consume and process Kafka events
- Why rejected: Full task queue is overkill for 2 simple consumers; adds Redis/RabbitMQ dependency

**Alternative C: APScheduler Background Tasks**
- Use APScheduler for periodic consumer polling
- Why rejected: Not needed; consumers run continuous consume loops natively

**Alternative D: Kubernetes Deployment Separation**
- Separate deployments for API and consumers
- Why rejected: Out of scope for Phase 006; can be addressed in future production-ready phase

## References

- Feature Spec: [specs/006-kafka-events/spec.md](../../specs/006-kafka-events/spec.md)
- Implementation Plan: [specs/006-kafka-events/plan.md](../../specs/006-kafka-events/plan.md) (AD-002)
- Related ADRs: [ADR-0001](./0001-kafka-infrastructure-stack.md), [ADR-0002](./0002-event-publishing-strategy.md)
- Evaluator Evidence: Research items R-004 and R-006 in research.md
