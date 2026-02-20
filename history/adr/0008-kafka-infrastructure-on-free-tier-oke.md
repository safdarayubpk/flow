# ADR-0008: Kafka Infrastructure on Free-Tier OKE

- **Status:** Accepted
- **Date:** 2026-02-19
- **Feature:** 008-oci-oke-cloud-deployment
- **Context:** The Flow Todo application uses Dapr pub/sub backed by Kafka for task event publishing (established in Phase V.3). Deploying Kafka to OKE requires fitting within a single VM.Standard.E2.1 node (1 OCPU, 8GB RAM) alongside the application workloads, Dapr system, NGINX ingress, and Kubernetes system components. The Kafka setup must be simple enough for a hackathon demo while providing data persistence across pod restarts.

## Decision

- **Kafka Deployment**: Simple Kubernetes Deployment (1 replica) — not StatefulSet or operator-managed
- **Zookeeper**: Separate Deployment (1 replica) — classic architecture, not KRaft mode
- **Images**: Confluent `cp-kafka:7.5.0` and `cp-zookeeper:7.5.0` (x86/amd64, matching node architecture)
- **Storage**: OCI Block Volume via `oci-bv` StorageClass, 5Gi PVC for Kafka data persistence
- **Resources**: Kafka 256Mi-512Mi RAM, Zookeeper 128Mi-256Mi RAM — tuned for free-tier budget
- **Topics**: Auto-create enabled (`auto.create.topics.enable=true`) for `task-events`

## Consequences

### Positive

- Simplest possible Kafka setup — easy to deploy, debug, and tear down
- PVC ensures data survives pod restarts without StatefulSet complexity
- Confluent images are well-tested and widely documented
- Resource footprint (~640Mi RAM total) fits within the free-tier budget
- No operator CRDs to install — reduces cluster resource overhead

### Negative

- No stable network identity — if the pod reschedules, in-flight messages could be lost (acceptable for hackathon)
- No ordered scaling or rolling updates — irrelevant for single-replica but limits future growth
- Zookeeper adds a second component; KRaft would eliminate it (but adds config complexity)
- Auto-create topics means no schema enforcement — topics created on first publish

## Alternatives Considered

- **Strimzi Operator**: Production-grade Kafka management but the operator alone consumes ~256Mi RAM — unacceptable overhead for free-tier. Designed for multi-broker clusters.
- **StatefulSet**: Provides stable pod identity and ordered scaling, but with exactly 1 replica these features add complexity without benefit. A Deployment + PVC achieves the same persistence.
- **Redpanda**: Lighter than Kafka (no Zookeeper needed) but introduces a new technology not used in prior phases, breaking continuity with the established Dapr + Kafka stack.
- **KRaft mode (no Zookeeper)**: Eliminates Zookeeper but requires Kafka 3.6+ configuration changes and is newer/less documented. Added config complexity outweighs the ~128Mi RAM savings.
- **emptyDir volume**: Simplest but data is lost on every pod restart, violating FR-008 (persistent Kafka data).
- **hostPath volume**: Ties data to a specific node and is problematic if the pod is rescheduled.

## References

- Feature Spec: [spec.md](../../specs/008-oci-oke-cloud-deployment/spec.md)
- Implementation Plan: [plan.md](../../specs/008-oci-oke-cloud-deployment/plan.md) (AD-3)
- Research: [research.md](../../specs/008-oci-oke-cloud-deployment/research.md) (R-2, R-5)
- Contracts: [kafka.yaml](../../specs/008-oci-oke-cloud-deployment/contracts/kafka.yaml)
- Related ADRs: [ADR-0001](0001-kafka-infrastructure-stack.md), [ADR-0005](0005-event-transport-migration-to-dapr-pub-sub.md)
