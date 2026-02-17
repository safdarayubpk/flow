# ADR-0005: Event Transport Migration to Dapr Pub/Sub

> **Scope**: Migration strategy from direct aiokafka producer to Dapr pub/sub, covering replacement approach, event envelope compatibility, and dependency cleanup.

- **Status:** Accepted
- **Date:** 2026-02-15
- **Feature:** 007-dapr-microservices
- **Context:** Phase V.2 (006-kafka-events) established event publishing via aiokafka with a singleton producer, fire-and-forget pattern, and single `todo-events` topic. Phase V.3 requires replacing this with Dapr pub/sub while maintaining the same Kafka broker underneath and preserving event envelope format for backward compatibility. The key decision is whether to do a clean replacement or keep aiokafka as a fallback.

## Decision

We will perform a **clean replacement** of aiokafka with Dapr pub/sub:

- **Migration Type**: Full replacement — aiokafka producer removed entirely, no fallback
- **Publishing Method**: `DaprClient().publish_event(pubsub_name="kafka-pubsub", topic_name="todo-events", data=event_json)`
- **Compatibility Wrapper**: New `fire_event()` function in `services/dapr/publisher.py` with identical signature to the old `kafka/producer.py` version
- **Event Envelope**: Same format preserved — `{event_type, timestamp, user_id, payload}`
- **User Isolation**: `user_id` propagated via Dapr `publish_metadata` on every event
- **Graceful Degradation**: Fire-and-forget preserved; exceptions caught and logged at WARNING level
- **Structured Logging**: INFO-level log for every publish with event_type, user_id, status
- **Dependency Change**: Remove `aiokafka>=0.10.0`, add `dapr>=1.14.0` + `dapr-ext-fastapi>=1.14.0`

## Consequences

### Positive

- Minimal code diff in service files (only import path changes from `kafka.producer` to `dapr.publisher`)
- Same Kafka broker underneath — Kafka UI still shows events, existing external consumers unaffected
- Broker-agnostic: future migration to different message broker requires zero code changes
- Clean codebase: no dead aiokafka code left behind
- Dapr sidecar handles connection management, retries, and serialization

### Negative

- No rollback path to aiokafka without re-adding the dependency and reverting imports
- Dapr wraps events in CloudEvents envelope — external consumers reading raw Kafka may see different wrapper
- DaprClient is synchronous (publish blocks briefly); mitigated by fire-and-forget wrapper
- Testing requires Dapr sidecar running (can't unit test publishing without Dapr)
- Slight increase in publish latency due to app-to-sidecar-to-Kafka hop (vs. direct app-to-Kafka)

## Alternatives Considered

**Alternative A: Transitional (keep aiokafka as fallback)**
- Publish via Dapr first; on failure, fall back to direct aiokafka
- Why rejected: Adds complexity, confuses debugging (which path was used?), maintains two dependencies. Clarification session confirmed clean replacement preferred.

**Alternative B: Feature-flagged toggle**
- ENV variable (`USE_DAPR_PUBSUB=true/false`) switches between Dapr and aiokafka
- Why rejected: Doubles testing surface, delays full migration, creates code branches that diverge over time.

**Alternative C: Gradual per-event-type migration**
- Migrate one event type at a time (e.g., `task-created` first, then `task-updated`, etc.)
- Why rejected: Increases migration duration, requires running both systems simultaneously, more error-prone than atomic switchover.

## References

- Feature Spec: [specs/007-dapr-microservices/spec.md](../../specs/007-dapr-microservices/spec.md) (FR-001, FR-002, FR-010)
- Implementation Plan: [specs/007-dapr-microservices/plan.md](../../specs/007-dapr-microservices/plan.md) (Phase B: T005-T010)
- Research: [specs/007-dapr-microservices/research.md](../../specs/007-dapr-microservices/research.md) (R4, R8)
- Supersedes: [ADR-0001](./0001-kafka-infrastructure-stack.md) (aiokafka replaced; Kafka infra retained), [ADR-0002](./0002-event-publishing-strategy.md) (publishing strategy preserved but transport changed)
- Clarification: spec.md Session 2026-02-15, Q2 (clean replacement confirmed)