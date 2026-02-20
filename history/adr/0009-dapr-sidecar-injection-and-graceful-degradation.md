# ADR-0009: Dapr Sidecar Injection and Graceful Degradation

- **Status:** Accepted
- **Date:** 2026-02-19
- **Feature:** 008-oci-oke-cloud-deployment
- **Context:** The Flow Todo backend uses Dapr for pub/sub event publishing (Phase V.3). Deploying Dapr to OKE requires installing the Dapr control plane and enabling sidecar injection on application pods. The existing Helm charts lack `podAnnotations` support needed for Dapr sidecar injection. The frontend does not use Dapr. The deployment must handle the case where Kafka/Dapr aren't fully ready when the backend starts, and the total Dapr footprint must fit within the free-tier node budget.

## Decision

- **Dapr Installation**: Official Helm chart (`dapr/dapr`) with aggressive resource limits (32Mi RAM / 10m CPU per component × 4 components = 128Mi total)
- **Sidecar Injection**: Backend only — controlled via pod annotations in `values-oci.yaml` (`dapr.io/enabled: "true"`, `dapr.io/app-id: "todo-backend"`, `dapr.io/app-port: "8000"`)
- **Frontend**: No Dapr sidecar — the frontend makes HTTP calls via ingress, not service invocation
- **Sidecar Resources**: 10m CPU / 32Mi RAM request, 100m CPU / 64Mi RAM limit per sidecar
- **Template Modification**: Add a minimal `podAnnotations` block to `k8s/backend/templates/deployment.yaml` (1 block, ~3 lines) rather than forking the chart
- **Graceful Degradation**: The backend's existing Dapr publisher code already handles sidecar unavailability — it logs a warning and skips event publishing. No code changes needed.

## Consequences

### Positive

- Backend continues serving CRUD operations normally even if Kafka/Dapr fail — users aren't blocked
- Minimal chart modification (podAnnotations support) rather than a full fork or rewrite
- Dapr annotations in values-oci.yaml keep the OCI-specific config separate from the base chart
- Frontend avoids unnecessary sidecar overhead (~64Mi RAM saved)
- Flexible deployment order — backend can start before Kafka is ready

### Negative

- Aggressive resource limits (32Mi per Dapr component) may cause OOMKills under unexpected load — acceptable for hackathon
- Template modification creates a divergence from the base Helm chart that must be maintained
- Graceful degradation means event publishing failures are silent — events may be lost without obvious user-facing errors
- Dapr control plane (4 components) adds ~128Mi RAM overhead even though only one pod uses it

## Alternatives Considered

- **Dapr CLI `dapr init -k`**: Installs Dapr with hardcoded defaults — no control over resource requests, would exceed free-tier budget
- **Skip Dapr entirely**: Would break the pub/sub event feature established in Phase V.3, losing the Kafka integration
- **Dapr on frontend too**: Unnecessary — the frontend doesn't use service invocation or pub/sub; adding a sidecar wastes ~64Mi RAM
- **Full Helm chart fork**: Maximum flexibility but high maintenance cost; the existing charts are simple enough that a one-block template addition suffices
- **Fail-fast (crash on Dapr unavailable)**: Would make deployment order critical and block users during Kafka startup — rejected in clarification session

## References

- Feature Spec: [spec.md](../../specs/008-oci-oke-cloud-deployment/spec.md) (FR-003, FR-014)
- Implementation Plan: [plan.md](../../specs/008-oci-oke-cloud-deployment/plan.md) (AD-2, AD-6)
- Research: [research.md](../../specs/008-oci-oke-cloud-deployment/research.md) (R-3)
- Contracts: [values-oci-backend.yaml](../../specs/008-oci-oke-cloud-deployment/contracts/values-oci-backend.yaml)
- Related ADRs: [ADR-0004](0004-dapr-runtime-and-sdk-integration.md), [ADR-0005](0005-event-transport-migration-to-dapr-pub-sub.md)
