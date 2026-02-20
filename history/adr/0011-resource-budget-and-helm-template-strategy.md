# ADR-0011: Resource Budget and Helm Template Strategy

- **Status:** Accepted
- **Date:** 2026-02-19
- **Feature:** 008-oci-oke-cloud-deployment
- **Context:** All workloads must fit on a single OCI VM.Standard.E2.1 node (1 OCPU / 8GB RAM). The total resource budget after Kubernetes system reservations (~600Mi) leaves approximately 7.5GB allocatable. The existing Helm charts for backend and frontend were designed for Minikube (Phase IV) and lack OCI-specific annotations and environment variables. A strategy is needed for extending the charts without breaking backward compatibility with the Minikube setup.

## Decision

- **Resource Budget Strategy**: Aggressive but validated resource requests totaling ~578m CPU / ~1364Mi RAM across all components:
  - Backend: 64m CPU / 128Mi RAM (+ Dapr sidecar: 10m CPU / 32Mi RAM)
  - Frontend: 64m CPU / 128Mi RAM
  - Kafka: 100m CPU / 256Mi RAM
  - Zookeeper: 50m CPU / 128Mi RAM
  - NGINX Ingress: 50m CPU / 64Mi RAM
  - Dapr control plane: 4 × 10m CPU / 4 × 32Mi RAM = 40m CPU / 128Mi RAM
  - K8s system: ~200m CPU / ~600Mi RAM (reserved by kubelet)
- **Helm Extension Strategy**: Use `values-oci.yaml` override files rather than modifying `values.yaml` defaults. Two minimal template changes required:
  1. Backend `deployment.yaml`: Add `podAnnotations` block from `.Values.podAnnotations` (enables Dapr sidecar injection)
  2. Frontend `deployment.yaml`: Add `BETTER_AUTH_URL` env var from `.Values.env.BETTER_AUTH_URL` (enables auth redirect)
- **No chart fork**: Templates remain backward-compatible — the new features are conditional (only active when values are provided)
- **Deployment approach**: Manual `helm upgrade --install` commands — no CI/CD, GitOps, or automation
- **Namespace**: Single `default` namespace for application workloads; `ingress-nginx` and `dapr-system` use dedicated namespaces per Helm chart convention

## Consequences

### Positive

- Total RAM request (~1364Mi) uses only 17% of the 8GB node — safe margin for burst usage
- `values-oci.yaml` keeps OCI-specific config isolated; Minikube setup remains unaffected
- Template changes are minimal (2 conditional blocks) — easy to review and maintain
- Single namespace simplifies RBAC, secret management, and kubectl commands for a hackathon
- Manual deployment keeps the procedure transparent and copy-pasteable

### Negative

- Aggressive resource limits may cause OOMKills under sustained load (e.g., Kafka broker restart, multiple concurrent chat requests)
- Two template modifications create a maintenance burden — must be applied on both Minikube and OCI branches
- No CI/CD means human error risk in deployment commands (typos, wrong order, missing steps)
- Single namespace provides no workload isolation — a misbehaving pod could affect others
- Manual LB IP substitution (`sed -i`) in values files is error-prone

## Alternatives Considered

- **Full Helm chart fork for OCI**: Maximum flexibility but doubles the chart maintenance. The existing charts are simple enough that 2 template additions are manageable.
- **Kustomize overlays instead of Helm values**: Would require restructuring the existing Helm-based setup; not worth the migration for a hackathon.
- **Multi-namespace isolation** (e.g., `app`, `messaging`, `infra`): Better isolation but adds NetworkPolicy complexity and cross-namespace service discovery overhead — overkill for a single-operator hackathon.
- **GitOps with ArgoCD/Flux**: Production-grade continuous delivery but adds significant cluster overhead (ArgoCD alone uses ~256Mi RAM) and setup complexity.
- **Higher resource requests** (production-like): Would risk node OOM with realistic production values (e.g., Kafka 1Gi, backend 512Mi).

## References

- Feature Spec: [spec.md](../../specs/008-oci-oke-cloud-deployment/spec.md) (Resource Budget table, Template Changes Required section)
- Implementation Plan: [plan.md](../../specs/008-oci-oke-cloud-deployment/plan.md) (AD-2, Risk Assessment)
- Data Model: [data-model.md](../../specs/008-oci-oke-cloud-deployment/data-model.md) (14 K8s resources, namespace topology)
- Contracts: [values-oci-backend.yaml](../../specs/008-oci-oke-cloud-deployment/contracts/values-oci-backend.yaml), [values-oci-frontend.yaml](../../specs/008-oci-oke-cloud-deployment/contracts/values-oci-frontend.yaml)
- Related ADRs: None
