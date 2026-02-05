# Implementation Plan: Local Kubernetes Deployment with Minikube

**Branch**: `004-k8s-minikube-deployment` | **Date**: 2026-01-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-k8s-minikube-deployment/spec.md`

## Summary

Deploy the existing Todo app (frontend Next.js + backend FastAPI) to a local Minikube Kubernetes cluster for beginner-level Kubernetes learning. The deployment uses Helm charts with security best practices, Kubernetes-native service discovery, and ConfigMaps/Secrets for environment management. All existing Vercel and Hugging Face deployments remain unaffected.

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript/JavaScript (frontend), YAML (Kubernetes manifests)
**Primary Dependencies**: Docker, Minikube v1.37.0, kubectl v1.35.x, Helm v4.1.0, kubectl-ai
**Storage**: Neon PostgreSQL (existing, reused via DATABASE_URL in Kubernetes Secret)
**Testing**: Manual verification via kubectl, minikube service, port-forward
**Target Platform**: Local Minikube Kubernetes cluster with Docker driver
**Project Type**: Web application (frontend + backend) containerized for Kubernetes
**Performance Goals**: App accessible within 5 minutes of deployment
**Constraints**: No Ingress, no in-cluster database, no changes to existing deployments, beginner-friendly
**Scale/Scope**: Single replica deployments, local development only

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-Driven Development | ✅ PASS | Spec and clarifications complete before planning |
| II. AI-Only Implementation | ✅ PASS | All code/YAML generated via Claude Code |
| III. Iterative Evolution | ✅ PASS | Phase IV builds on Phase II-III without breaking them |
| IV. Reusability and Modularity | ✅ PASS | Helm charts are reusable, skills invoked |
| V. Security and Isolation | ✅ PASS | Security context applied (runAsNonRoot, readOnlyRootFilesystem) |
| VI. Cloud-Native Readiness | ✅ PASS | Kubernetes deployment with externalized config |

## Project Structure

### Documentation (this feature)

```text
specs/004-k8s-minikube-deployment/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output (N/A - no new data models)
├── quickstart.md        # Phase 1 output (deployment guide)
├── contracts/           # Phase 1 output (Kubernetes manifests)
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
# Kubernetes deployment files (new)
k8s/
├── backend/
│   ├── Chart.yaml           # Helm chart metadata
│   ├── values.yaml          # Configurable values
│   └── templates/
│       ├── deployment.yaml  # Backend Deployment
│       ├── service.yaml     # Backend Service
│       ├── configmap.yaml   # Non-sensitive config
│       └── secret.yaml      # Sensitive config (DATABASE_URL, etc.)
├── frontend/
│   ├── Chart.yaml           # Helm chart metadata
│   ├── values.yaml          # Configurable values
│   └── templates/
│       ├── deployment.yaml  # Frontend Deployment
│       ├── service.yaml     # Frontend Service
│       └── configmap.yaml   # API URL config
└── scripts/
    ├── build-images.sh      # Build Docker images
    ├── load-images.sh       # Load images to Minikube
    └── deploy.sh            # Deploy Helm charts

# Dockerfiles (new, separate from existing)
backend/
├── Dockerfile               # Existing (Hugging Face Spaces - DO NOT MODIFY)
└── Dockerfile.k8s           # New (Kubernetes deployment)

frontend/
└── Dockerfile.k8s           # New (Kubernetes deployment)

# Existing structure (unchanged)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/
```

**Structure Decision**: Web application with separate Helm charts for frontend and backend. New Dockerfile.k8s files created to avoid modifying existing Hugging Face deployment. All Kubernetes manifests in dedicated k8s/ directory.

## Architecture Decisions

### ADR Alignment

| ADR | Impact on Phase IV |
|-----|-------------------|
| ADR-001: JWT Storage | JWT cookies work unchanged; frontend-backend communication via K8s service names |
| ADR-002: User Isolation | WHERE user_id filter unchanged; runs in K8s pods |
| ADR-003: Soft Delete | deleted_at logic unchanged; uses same Neon database |

### Key Design Decisions

1. **Separate Dockerfiles**: Create `Dockerfile.k8s` files instead of modifying existing `Dockerfile` to preserve Hugging Face Spaces deployment.

2. **Helm Charts over Plain Manifests**: Use Helm for templating, configurability, and alignment with helm-chart-todo-app skill.

3. **ConfigMaps and Secrets**:
   - ConfigMap: Non-sensitive config (LOG_LEVEL, backend service URL)
   - Secret: Sensitive config (DATABASE_URL, JWT_SECRET, API keys)

4. **Service Discovery**: Frontend communicates with backend via `todo-backend-service.default.svc.cluster.local`

5. **Security Context**: All pods run with:
   - runAsNonRoot: true
   - runAsUser: 1000
   - readOnlyRootFilesystem: true
   - resource limits defined

6. **Local Access**: Use `minikube service` or `kubectl port-forward` (no Ingress)

## Skills to Invoke

| Skill | Usage |
|-------|-------|
| kubernetes-yaml-best-practices | Deployment/Service YAML generation |
| helm-chart-todo-app | Helm chart structure and values |
| minikube-local-deployment-pattern | Image loading, debugging, port-forward |
| k8s-security-basics | Security context configuration |

## Complexity Tracking

> No violations - all decisions align with constitution principles.

| Item | Justification |
|------|---------------|
| Separate Dockerfile.k8s | Required to preserve existing Hugging Face deployment |
| Helm charts | Preferred per spec; provides templating and configurability |
| Neon database reuse | Clarified decision - avoids complexity of in-cluster database |
