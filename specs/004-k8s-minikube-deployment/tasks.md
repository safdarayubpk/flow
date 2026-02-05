# Tasks: Local Kubernetes Deployment with Minikube

**Input**: Design documents from `/specs/004-k8s-minikube-deployment/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, contracts/ ✅, quickstart.md ✅

**Tests**: Not explicitly requested - tasks focus on deployment infrastructure.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/` (FastAPI)
- **Frontend**: `frontend/` (Next.js)
- **Kubernetes**: `k8s/backend/`, `k8s/frontend/`, `k8s/scripts/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create Kubernetes directory structure and helper scripts

- [x] T001 Create k8s/ directory structure per plan.md at k8s/
- [x] T002 [P] Create backend Helm chart skeleton at k8s/backend/Chart.yaml
- [x] T003 [P] Create frontend Helm chart skeleton at k8s/frontend/Chart.yaml
- [x] T004 [P] Create build-images.sh script at k8s/scripts/build-images.sh
- [x] T005 [P] Create load-images.sh script at k8s/scripts/load-images.sh
- [x] T006 [P] Create deploy.sh script at k8s/scripts/deploy.sh

---

## Phase 2: User Story 2 - Containerize Frontend and Backend (Priority: P1)

**Goal**: Create Dockerfile.k8s files for both frontend and backend without modifying existing HuggingFace Dockerfile

**Independent Test**: Build images locally with `docker build` and verify they start correctly

### Implementation for User Story 2

- [x] T007 [P] [US2] Create backend Dockerfile.k8s with multi-stage build at backend/Dockerfile.k8s
- [x] T008 [P] [US2] Create frontend Dockerfile.k8s with multi-stage build at frontend/Dockerfile.k8s
- [x] T009 [US2] Add health endpoint /api/health to frontend if not exists at frontend/src/app/api/health/route.ts
- [x] T010 [US2] Verify backend /health endpoint exists at backend/src/main.py
- [x] T011 [US2] Test Docker image builds locally with docker build commands

**Checkpoint**: Both images build successfully and can be run with `docker run`

---

## Phase 3: User Story 1 - Deploy Full Todo App to Minikube (Priority: P1) 🎯 MVP

**Goal**: Deploy both services to Minikube using Helm charts with proper configuration

**Independent Test**: Deploy to Minikube and verify pods are running with `kubectl get pods`

### Implementation for User Story 1

#### Backend Helm Chart

- [x] T012 [P] [US1] Create backend values.yaml with image, service, and security config at k8s/backend/values.yaml
- [x] T013 [P] [US1] Create backend deployment.yaml template at k8s/backend/templates/deployment.yaml
- [x] T014 [P] [US1] Create backend service.yaml template at k8s/backend/templates/service.yaml
- [x] T015 [P] [US1] Create backend configmap.yaml template at k8s/backend/templates/configmap.yaml
- [x] T016 [US1] Create backend secret.yaml template (DATABASE_URL, JWT_SECRET, etc.) at k8s/backend/templates/secret.yaml

#### Frontend Helm Chart

- [x] T017 [P] [US1] Create frontend values.yaml with image, service, and security config at k8s/frontend/values.yaml
- [x] T018 [P] [US1] Create frontend deployment.yaml template at k8s/frontend/templates/deployment.yaml
- [x] T019 [P] [US1] Create frontend service.yaml template at k8s/frontend/templates/service.yaml
- [x] T020 [P] [US1] Create frontend configmap.yaml template at k8s/frontend/templates/configmap.yaml

#### Deployment Tasks

- [x] T021 [US1] Load images to Minikube with minikube image load commands
- [x] T022 [US1] Create Kubernetes secret with kubectl create secret for sensitive values
- [x] T023 [US1] Deploy backend Helm chart with helm install todo-backend ./k8s/backend
- [x] T024 [US1] Deploy frontend Helm chart with helm install todo-frontend ./k8s/frontend
- [x] T025 [US1] Verify all pods are running with kubectl get pods

**Checkpoint**: Both services deployed to Minikube with pods in Running state

---

## Phase 4: User Story 3 - Configure Service Communication (Priority: P2)

**Goal**: Ensure frontend communicates with backend via Kubernetes service DNS name

**Independent Test**: Make API call from frontend pod to backend service and verify response

### Implementation for User Story 3

- [x] T026 [US3] Configure NEXT_PUBLIC_API_URL in frontend configmap to use http://todo-backend-service:8000
- [x] T027 [US3] Verify frontend-backend communication by testing API calls
- [x] T028 [US3] Test AI chatbot functionality works through K8s networking

**Checkpoint**: Frontend successfully calls backend API using Kubernetes service name

---

## Phase 5: User Story 4 - Access Deployed Application Locally (Priority: P2)

**Goal**: Provide local access to the deployed application via port-forward or minikube service

**Independent Test**: Access application in browser and verify UI loads

### Implementation for User Story 4

- [x] T029 [US4] Test access via minikube service todo-frontend-service command
- [x] T030 [US4] Test access via kubectl port-forward svc/todo-frontend-service 3000:80
- [x] T031 [US4] Verify full app functionality: login, AI chatbot, task management

**Checkpoint**: Application accessible locally with all features working

---

## Phase 6: User Story 5 - Use kubectl-ai for YAML (Priority: P3)

**Goal**: Use kubectl-ai to explain or debug Kubernetes YAML for learning purposes

**Independent Test**: Run kubectl-ai command and verify useful output

### Implementation for User Story 5

- [x] T032 [US5] Use kubectl-ai to explain backend deployment.yaml structure
- [x] T033 [US5] Document kubectl-ai usage example in quickstart.md if not present

**Checkpoint**: kubectl-ai requirement satisfied (FR-011)

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation and validation

- [x] T034 [P] Update quickstart.md with any discovered improvements
- [x] T035 [P] Add inline comments to all Kubernetes YAML files for beginners
- [x] T036 Validate all success criteria from spec.md (SC-001 through SC-007)
- [x] T037 Verify existing Vercel and HuggingFace deployments remain unchanged

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **User Story 2 (Phase 2)**: Depends on Setup - creates Docker images
- **User Story 1 (Phase 3)**: Depends on US2 - needs images to deploy
- **User Story 3 (Phase 4)**: Depends on US1 - needs deployed services
- **User Story 4 (Phase 5)**: Depends on US3 - needs working communication
- **User Story 5 (Phase 6)**: Can run after US1 is deployed
- **Polish (Phase 7)**: Depends on all user stories complete

### Critical Path

```
Setup → US2 (Dockerfiles) → US1 (Helm Charts) → US3 (Communication) → US4 (Access)
                                              ↘
                                               US5 (kubectl-ai) → Polish
```

### User Story Dependencies

| Story | Depends On | Can Parallel With |
|-------|------------|-------------------|
| US2 | Setup | - |
| US1 | US2 | - |
| US3 | US1 | US5 |
| US4 | US3 | US5 |
| US5 | US1 | US3, US4 |

### Parallel Opportunities

- T002, T003: Backend and frontend Chart.yaml can be created in parallel
- T004, T005, T006: All scripts can be created in parallel
- T007, T008: Both Dockerfiles can be created in parallel
- T012-T016: Backend Helm templates can be created in parallel
- T017-T020: Frontend Helm templates can be created in parallel
- T034, T035: Documentation tasks can run in parallel

---

## Parallel Example: Phase 1 Setup

```bash
# Launch all setup tasks together:
Task: "Create backend Helm chart skeleton at k8s/backend/Chart.yaml"
Task: "Create frontend Helm chart skeleton at k8s/frontend/Chart.yaml"
Task: "Create build-images.sh script at k8s/scripts/build-images.sh"
Task: "Create load-images.sh script at k8s/scripts/load-images.sh"
Task: "Create deploy.sh script at k8s/scripts/deploy.sh"
```

---

## Parallel Example: Backend Helm Templates

```bash
# Launch all backend template tasks together:
Task: "Create backend values.yaml at k8s/backend/values.yaml"
Task: "Create backend deployment.yaml template at k8s/backend/templates/deployment.yaml"
Task: "Create backend service.yaml template at k8s/backend/templates/service.yaml"
Task: "Create backend configmap.yaml template at k8s/backend/templates/configmap.yaml"
```

---

## Implementation Strategy

### MVP First (User Stories 1-2)

1. Complete Phase 1: Setup
2. Complete Phase 2: User Story 2 (Dockerfiles)
3. Complete Phase 3: User Story 1 (Helm Charts + Deploy)
4. **STOP and VALIDATE**: Verify pods are running
5. Continue to US3, US4 for full functionality

### Incremental Delivery

1. Setup + US2 → Docker images ready
2. Add US1 → Services deployed to Minikube
3. Add US3 → Frontend-backend communication working
4. Add US4 → App accessible locally (MVP complete!)
5. Add US5 → kubectl-ai learning completed
6. Polish → Documentation finalized

---

## Summary

| Metric | Count |
|--------|-------|
| Total Tasks | 37 |
| Setup Tasks | 6 |
| US2 (Containerization) | 5 |
| US1 (Deployment) | 14 |
| US3 (Communication) | 3 |
| US4 (Access) | 3 |
| US5 (kubectl-ai) | 2 |
| Polish Tasks | 4 |
| Parallel Opportunities | 18 tasks marked [P] |

### MVP Scope

**Minimum Viable Deployment**: Complete through User Story 4 (T001-T031)
- Docker images built and loaded
- Helm charts deployed
- Services communicating
- Application accessible locally

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story
- Preserve existing backend/Dockerfile for HuggingFace Spaces
- Use skills: kubernetes-yaml-best-practices, helm-chart-todo-app, minikube-local-deployment-pattern, k8s-security-basics
- Security context: runAsNonRoot, readOnlyRootFilesystem, resource limits on all pods
- Commit after each phase or logical group
