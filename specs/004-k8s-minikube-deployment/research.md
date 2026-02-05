# Research: Local Kubernetes Deployment with Minikube

**Branch**: `004-k8s-minikube-deployment` | **Date**: 2026-01-27

## Research Summary

All technical context items have been resolved through specification clarifications and existing project knowledge. No NEEDS CLARIFICATION items remain.

---

## Decision 1: Dockerfile Strategy for Kubernetes

**Decision**: Create separate `Dockerfile.k8s` files for both frontend and backend

**Rationale**:
- Existing `backend/Dockerfile` is configured for Hugging Face Spaces (port 7860, specific user requirements)
- Kubernetes deployment needs different configuration (port 8000, security context compatibility)
- Separation ensures zero risk to existing production deployment

**Alternatives Considered**:
1. **Modify existing Dockerfile with multi-stage/args**: Rejected - risk of breaking Hugging Face deployment
2. **Use same Dockerfile with different CMD**: Rejected - port and user requirements differ
3. **Separate Dockerfile.k8s**: Chosen - clean separation, no risk to existing deployments

---

## Decision 2: Helm Chart Structure

**Decision**: Create two separate Helm charts (backend and frontend) in `k8s/` directory

**Rationale**:
- Aligns with helm-chart-todo-app skill patterns
- Allows independent deployment and scaling of each service
- Provides templating for environment-specific values
- Follows Kubernetes best practices for microservices

**Alternatives Considered**:
1. **Single umbrella chart**: Rejected - over-complicated for beginner learning
2. **Plain YAML manifests**: Rejected - spec prefers Helm charts
3. **Two separate charts**: Chosen - clear separation, skill alignment, beginner-friendly

---

## Decision 3: Environment Configuration Pattern

**Decision**: Use Kubernetes ConfigMaps for non-sensitive config and Secrets for sensitive config

**Rationale**:
- ConfigMap: LOG_LEVEL, BACKEND_URL (for frontend)
- Secret: DATABASE_URL, JWT_SECRET, OPENAI_API_KEY, BETTER_AUTH_SECRET
- Standard Kubernetes pattern for configuration management
- Aligns with FR-015 clarification

**Alternatives Considered**:
1. **Bake into Docker image**: Rejected - not configurable, security risk
2. **External config service**: Rejected - over-complicated for local deployment
3. **ConfigMap + Secret**: Chosen - standard pattern, proper security separation

---

## Decision 4: Service Communication Pattern

**Decision**: Use Kubernetes native DNS service discovery

**Rationale**:
- Frontend accesses backend via `http://todo-backend-service:8000` (short form within namespace)
- Full DNS: `todo-backend-service.default.svc.cluster.local`
- Standard Kubernetes networking pattern
- Aligns with FR-016 clarification

**Alternatives Considered**:
1. **Environment variables**: Rejected - less flexible, harder to manage
2. **Service mesh (Istio)**: Rejected - over-complicated for beginner learning
3. **Native DNS**: Chosen - simple, standard, well-documented

---

## Decision 5: Security Context Configuration

**Decision**: Apply basic security context following k8s-security-basics skill

**Rationale**:
- Pod-level: runAsNonRoot, runAsUser: 1000, fsGroup: 1000
- Container-level: readOnlyRootFilesystem, allowPrivilegeEscalation: false
- Resource limits: memory and CPU requests/limits
- Aligns with FR-014 clarification

**Alternatives Considered**:
1. **No security context**: Rejected - violates constitution principle V
2. **Restricted PSS**: Rejected - may require writable paths for app functionality
3. **Basic security context**: Chosen - good balance of security and compatibility

---

## Decision 6: Local Access Method

**Decision**: Support both `minikube service` and `kubectl port-forward`

**Rationale**:
- `minikube service todo-frontend-service`: Opens browser automatically
- `kubectl port-forward svc/todo-frontend-service 3000:80`: Manual control
- Both documented in quickstart.md for learning purposes

**Alternatives Considered**:
1. **Ingress**: Rejected - spec explicitly excludes Ingress
2. **NodePort only**: Rejected - requires knowing Minikube IP
3. **Both methods**: Chosen - flexible, educational

---

## Decision 7: Image Naming Convention

**Decision**: Use `todo-backend:k8s` and `todo-frontend:k8s` for Kubernetes images

**Rationale**:
- Clear distinction from existing images (if any)
- `k8s` suffix indicates Kubernetes-specific build
- Simple naming for beginner understanding

**Alternatives Considered**:
1. **Version tags (1.0.0)**: Rejected - overkill for local development
2. **latest tag**: Rejected - ambiguous, not recommended
3. **k8s suffix**: Chosen - clear, descriptive

---

## Technical Research: kubectl-ai Usage

**Decision**: Use kubectl-ai to explain Deployment YAML structure

**Rationale**:
- Requirement FR-011 mandates at least one kubectl-ai usage
- Explaining YAML provides educational value for beginners
- Example: `kubectl-ai "explain this deployment yaml" < deployment.yaml`

**Planned Usage**:
```bash
# During task implementation, use kubectl-ai to explain generated YAML
kubectl-ai "explain what this kubernetes deployment does and why each field is important" < k8s/backend/templates/deployment.yaml
```

---

## Dependencies Verified

| Dependency | Version | Status |
|------------|---------|--------|
| Docker Desktop | Running | ✅ Pre-verified |
| Minikube | v1.37.0 | ✅ Pre-verified |
| kubectl | v1.35.x | ✅ Pre-verified |
| Helm | v4.1.0 | ✅ Pre-verified |
| kubectl-ai | Installed | ✅ Pre-verified |

---

## Outstanding Items

None. All research complete and decisions documented.
