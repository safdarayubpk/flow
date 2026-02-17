# ADR-0001: Kafka Infrastructure Stack

> **Scope**: Local development Kafka infrastructure for event-driven architecture in the Todo application.

- **Status:** Accepted
- **Date:** 2026-02-10
- **Feature:** 006-kafka-events
- **Context:** The Todo application needs Kafka for event publishing and consumption. The decision involves selecting Docker images, Kafka client library, and local development tooling that work together as an integrated solution.

## Decision

We will use the following integrated Kafka infrastructure stack:

- **Docker Images**: Confluent Platform (cp-zookeeper:7.5.0, cp-kafka:7.5.0)
- **Python Client**: aiokafka>=0.10.0 (async-native Kafka client)
- **Visualization**: provectuslabs/kafka-ui (for event inspection)
- **Configuration**: docker-compose.kafka.yml at repository root
- **Topic**: Single `todo-events` topic for all event types

## Consequences

### Positive

- Confluent images are production-grade with consistent versioning
- aiokafka integrates natively with FastAPI's async model (no thread pool needed)
- Kafka UI enables visual event inspection for debugging
- Single `docker-compose up` starts the entire Kafka infrastructure
- Active maintenance and good documentation for all components

### Negative

- Requires Docker for local development
- Zookeeper adds resource overhead (vs. KRaft mode in newer Kafka)
- aiokafka has smaller community than confluent-kafka
- Confluent images are larger than alternatives like Bitnami

## Alternatives Considered

**Alternative Stack A: Bitnami + kafka-python**
- Bitnami/kafka images + synchronous kafka-python client
- Why rejected: kafka-python is synchronous, would require thread pool executor in async FastAPI app

**Alternative Stack B: Redpanda + confluent-kafka**
- Redpanda (Kafka-compatible, no Zookeeper) + confluent-kafka (C library)
- Why rejected: Different ecosystem, C library adds build complexity, overkill for beginner-friendly scope

**Alternative Stack C: faust Streaming Framework**
- Full streaming framework with built-in consumer patterns
- Why rejected: Heavyweight for simple event publishing; adds unnecessary abstraction

## References

- Feature Spec: [specs/006-kafka-events/spec.md](../../specs/006-kafka-events/spec.md)
- Implementation Plan: [specs/006-kafka-events/plan.md](../../specs/006-kafka-events/plan.md)
- Related ADRs: None (first Kafka-related decision)
- Evaluator Evidence: Research items R-001 and R-002 in research.md
