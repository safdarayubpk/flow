# Research: Kafka Event-Driven Architecture

**Feature**: 006-kafka-events | **Date**: 2026-02-10

## Research Items

### R-001: aiokafka Compatibility with Python 3.13

**Decision**: Use aiokafka>=0.10.0

**Rationale**:
- aiokafka is the standard async Kafka client for Python
- Version 0.10.0+ supports Python 3.10-3.13
- Actively maintained with good FastAPI integration examples
- kafka-producer-pattern and kafka-consumer-pattern skills already use aiokafka

**Alternatives Considered**:
- `kafka-python`: Synchronous, would require thread pool executor
- `confluent-kafka`: More complex, C library dependency
- `faust`: Full streaming framework, overkill for simple event publishing

### R-002: Docker Compose Kafka Setup for Local Development

**Decision**: Use Confluent Platform images (cp-zookeeper, cp-kafka)

**Rationale**:
- Confluent images are production-grade and well-documented
- Consistent versioning (7.5.0 for both)
- Smaller footprint than full Confluent Platform
- provectuslabs/kafka-ui provides visual event inspection

**Alternatives Considered**:
- `bitnami/kafka`: Good alternative, less documentation
- `wurstmeister/kafka`: Older, less maintained
- `redpanda`: Kafka-compatible, no Zookeeper, but different ecosystem

### R-003: Event Publishing Pattern (Sync vs Async)

**Decision**: Fire-and-forget async publishing with graceful failure handling

**Rationale**:
- Non-blocking: task operations must not wait for Kafka
- Graceful degradation: application works without Kafka
- Simple implementation: no retry logic, no outbox pattern
- Appropriate for local development focus

**Alternatives Considered**:
- Transactional outbox: Guarantees delivery, but adds DB complexity
- Sync publishing with retry: Blocks operations, violates fire-and-forget requirement
- Message queue with acknowledgment: Overkill for this phase

### R-004: Consumer Execution Model

**Decision**: FastAPI background tasks via lifespan

**Rationale**:
- Single deployment unit (no separate worker processes)
- Beginner-friendly (one `docker-compose up` starts everything)
- Aligns with existing recurring task scheduler pattern in main.py
- Consumers share same process, simplifying debugging

**Alternatives Considered**:
- Separate worker scripts: More production-like, but adds deployment complexity
- Celery: Full task queue, overkill for 2 simple consumers
- APScheduler: Not needed, consumers run continuously

### R-005: Event Schema Versioning

**Decision**: No schema versioning for this phase (implicit v1)

**Rationale**:
- Single local deployment, no compatibility concerns
- All producers and consumers deploy together
- Schema registry explicitly out of scope
- Simplicity for beginners

**Alternatives Considered**:
- JSON Schema validation: Good practice, but adds complexity
- Avro with schema registry: Production-grade, out of scope
- Version field in events: Could add later if needed

### R-006: Consumer Idempotency Strategy

**Decision**: Use task_id as natural idempotency key; check database before action

**Rationale**:
- Recurring Consumer: Check if task instance already exists before creating
- Notification Consumer: Logging is inherently idempotent
- Simple implementation without additional state storage

**Alternatives Considered**:
- Event ID deduplication table: More robust, but adds DB schema
- Redis-based deduplication: External dependency
- Consumer offset tracking: Not persisted across restarts per spec

## Best Practices Applied

### From kafka-producer-pattern Skill

1. Singleton producer via `get_producer()` function
2. `produce_event()` helper with standard event structure
3. Environment-based configuration with fallback to disabled
4. JSON serialization with value_serializer

### From kafka-consumer-pattern Skill

1. `KafkaEventConsumer` class with handler registration
2. Consumer group IDs for parallel scaling (future)
3. Manual commit after successful processing
4. Graceful error handling (log and skip malformed events)

## Unresolved Items

None. All NEEDS CLARIFICATION items from spec have been resolved.
