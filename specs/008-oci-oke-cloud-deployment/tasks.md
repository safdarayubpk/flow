# Tasks: OCI OKE Cloud Deployment

**Input**: Design documents from `/specs/008-oci-oke-cloud-deployment/`
**Prerequisites**: plan.md (complete), spec.md (complete), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Not requested — no automated test tasks included. Verification is manual via kubectl and curl.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Kubernetes manifests**: `k8s/` at repository root
- **Backend Helm chart**: `k8s/backend/`
- **Frontend Helm chart**: `k8s/frontend/`
- **Contracts (canonical source)**: `specs/008-oci-oke-cloud-deployment/contracts/`

---

## Phase 1: Setup (Cluster Access & Helm Repos)

**Purpose**: Verify OKE cluster access and prepare Helm repositories
- [x] T001 Verify MFA session and cluster access by running `kubectl get nodes` — expect 1 node in Ready state
- [x] T002 Add Helm repos: `ingress-nginx` from `https://kubernetes.github.io/ingress-nginx` and `dapr` from `https://dapr.github.io/helm-charts`, then run `helm repo update`

---

## Phase 2: Foundational (Infrastructure & Manifest Creation)

**Purpose**: Install cluster infrastructure and create all Kubernetes manifests. MUST complete before any user story deployment.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

### Infrastructure Installation

- [x] T003 Install NGINX Ingress Controller via Helm with OCI LB annotations (flexible shape 10Mbps, LB subnet OCID, admission webhooks disabled, resource requests 50m/64Mi) into namespace `ingress-nginx` — use exact command from spec.md Step 2
- [x] T004 Wait for OCI Load Balancer IP assignment on `ingress-nginx-controller` service, then export `LB_IP` environment variable — use spec.md Step 3
- [x] T005 Install Dapr via Helm into namespace `dapr-system` with resource limits (10m CPU / 32Mi RAM per component × 4) — use exact command from spec.md Step 4. Verify with `kubectl get pods -n dapr-system`

### Manifest Creation (parallelizable — different files)

- [x] T006 [P] Create Kafka + Zookeeper manifest at `k8s/kafka.yaml` from contract `specs/008-oci-oke-cloud-deployment/contracts/kafka.yaml` — includes PVC (oci-bv, 5Gi), Zookeeper Deployment+Service, Kafka Deployment+Service with volume mount
- [x] T007 [P] Create Dapr pub/sub component manifest at `k8s/dapr-kafka-pubsub.yaml` from contract `specs/008-oci-oke-cloud-deployment/contracts/dapr-kafka-pubsub.yaml` — Component CRD pointing to `kafka.default.svc.cluster.local:9092`
- [x] T008 [P] Create Ingress manifest at `k8s/ingress.yaml` from contract `specs/008-oci-oke-cloud-deployment/contracts/ingress.yaml` — regex rewrite `/api(/|$)(.*)` → backend:8000, `/(.*)` → frontend:80

### Helm Template Modifications (parallelizable — different files)

- [x] T009 [P] Add `podAnnotations` support to `k8s/backend/templates/deployment.yaml` — insert `{{- with .Values.podAnnotations }}` / `annotations:` / `{{- toYaml . | nindent 8 }}` / `{{- end }}` block under `spec.template.metadata` (after `labels:` block, before `spec:`)
- [x] T010 [P] Add `BETTER_AUTH_URL` env var support to `k8s/frontend/templates/deployment.yaml` — insert conditional `{{- if .Values.env.BETTER_AUTH_URL }}` env block after the `NEXT_PUBLIC_API_URL` env entry

### Values Override Files (parallelizable — different files, depends on T004 for LB_IP)

- [x] T011 [P] Create `k8s/backend/values-oci.yaml` from contract `specs/008-oci-oke-cloud-deployment/contracts/values-oci-backend.yaml` — substitute `<LB_IP>` with actual LoadBalancer IP in `CORS_ORIGINS`
- [x] T012 [P] Create `k8s/frontend/values-oci.yaml` from contract `specs/008-oci-oke-cloud-deployment/contracts/values-oci-frontend.yaml` — substitute `<LB_IP>` with actual LoadBalancer IP in `NEXT_PUBLIC_API_URL` and `BETTER_AUTH_URL`

### Deploy Infrastructure Components

- [x] T013 Deploy Kafka + Zookeeper by running `kubectl apply -f k8s/kafka.yaml` — wait for both pods ready with `kubectl wait --for=condition=ready pod -l app=zookeeper --timeout=120s` and `kubectl wait --for=condition=ready pod -l app=kafka --timeout=120s`
- [x] T014 Deploy Dapr pub/sub component by running `kubectl apply -f k8s/dapr-kafka-pubsub.yaml`
- [x] T015 Create Kubernetes Secrets with `kubectl create secret generic todo-secrets` containing DATABASE_URL, SECRET_KEY, BETTER_AUTH_SECRET, GROQ_API_KEY, OPENAI_API_KEY — use placeholder values from spec.md Step 7, replace with real values from `.env`

**Checkpoint**: Infrastructure ready — NGINX Ingress with LB IP, Dapr running, Kafka running, secrets created, manifests prepared. User story deployment can begin.

---

## Phase 3: User Story 1 + 2 — Cloud App Access & API Routing (Priority: P1) 🎯 MVP

**Goal**: Deploy backend and frontend to OKE, apply ingress routing, and verify the application is accessible via the LoadBalancer IP. US1 and US2 are combined because they share the same deployment steps and are both P1.

**Independent Test (US1)**: Open `http://<LB_IP>` in a browser, sign up, create a task, verify it persists.
**Independent Test (US2)**: Run `curl http://<LB_IP>/api/health` and verify HTTP 200 response.

### Implementation

- [x] T016 [US1] [US2] Deploy backend with `helm upgrade --install todo-backend ./k8s/backend --values k8s/backend/values-oci.yaml` — verify pod is Running with `kubectl get pods -l app.kubernetes.io/name=todo-backend`
- [x] T017 [US1] [US2] Deploy frontend with `helm upgrade --install todo-frontend ./k8s/frontend --values k8s/frontend/values-oci.yaml` — verify pod is Running with `kubectl get pods -l app.kubernetes.io/name=todo-frontend`
- [x] T018 [US1] [US2] Apply Ingress resource with `kubectl apply -f k8s/ingress.yaml` — verify with `kubectl get ingress todo-ingress` and confirm ADDRESS matches LB_IP
- [x] T019 [US2] Verify backend health: `curl http://$LB_IP/api/health` returns HTTP 200 — check backend logs with `kubectl logs -l app.kubernetes.io/name=todo-backend -c todo-backend --tail=50` for startup errors
- [x] T020 [US1] Verify frontend loads: `curl -s http://$LB_IP | head -20` returns HTML — open `http://<LB_IP>` in browser, sign up, log in, create a task
- [x] T021 [US1] [US2] Verify service names match ingress expectations: run `kubectl get svc` and confirm `todo-backend-todo-backend:8000` and `todo-frontend-todo-frontend:80` exist — if names differ, update `k8s/ingress.yaml` backend service names and reapply
- [x] T022 [US1] If frontend API calls fail (browser console shows wrong URL), apply NEXT_PUBLIC_API_URL fix: either use relative `/api` paths or rebuild Docker image with `--build-arg NEXT_PUBLIC_API_URL=http://$LB_IP/api` per quickstart.md Known Risk section

**Checkpoint**: MVP complete — US1 (frontend accessible, auth works, task CRUD) and US2 (backend API health, ingress routing) are both functional.

---

## Phase 4: User Story 3 — Event-Driven Task Processing (Priority: P2)

**Goal**: Verify that task events are published to Kafka via Dapr when tasks are created or modified.

**Independent Test**: Create a task via the frontend, then check backend logs for Dapr pub/sub event publishing confirmation.

### Implementation

- [x] T023 [US3] Verify Dapr sidecar is running in backend pod: `kubectl get pods -l app.kubernetes.io/name=todo-backend -o jsonpath='{.items[0].spec.containers[*].name}'` should list both `todo-backend` and `daprd`
- [x] T024 [US3] Verify Kafka topic existence: `kubectl exec deploy/kafka -- kafka-topics --bootstrap-server localhost:9092 --list` should show `task-events` (created on first publish if auto-create enabled)
- [x] T025 [US3] Test event publishing: create a task via `http://<LB_IP>`, then check backend logs with `kubectl logs -l app.kubernetes.io/name=todo-backend -c todo-backend --tail=30 | grep -i "publish\|event\|dapr"` for successful pub/sub event log entries
- [x] T026 [US3] If Dapr sidecar not present: verify `podAnnotations` in `k8s/backend/values-oci.yaml` include `dapr.io/enabled: "true"` and that template modification T009 was applied correctly — redeploy backend if needed

**Checkpoint**: US3 complete — events flow from backend through Dapr sidecar to Kafka broker.

---

## Phase 5: User Story 4 — Operator Deployment & Management (Priority: P2)

**Goal**: Verify the documented deployment and teardown procedures work end-to-end.

**Independent Test**: Run the teardown procedure, then redeploy from step 1 — all components should come up healthy.

### Implementation

- [x] T027 [US4] Run full verification suite from spec.md Step 13: `kubectl get pods` (all Running), `kubectl get svc` (correct ports), `kubectl get ingress` (LB IP assigned), `curl http://$LB_IP/api/health` (200), `curl http://$LB_IP` (HTML), backend logs clean
- [x] T028 [US4] Test MFA session refresh: wait for session expiry or force re-auth with `oci session authenticate --region me-dubai-1 --profile-name OKE_SESSION`, then verify kubectl operations resume with `kubectl get nodes`
- [x] T029 [US4] Test teardown procedure: run all teardown commands from spec.md Teardown Procedure section in order — verify clean state with `kubectl get pods`, `kubectl get svc`, `kubectl get pvc` returning no application resources
- [x] T030 [US4] Test redeployment: after teardown (T029), redeploy from Phase 1 Step T001 through Phase 3 — verify all components come up healthy. Note: new LB IP will be assigned, requiring values-oci.yaml updates

**Checkpoint**: US4 complete — operator can deploy, verify, tear down, and redeploy the full stack.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final cleanup and documentation validation

- [x] T031 Validate resource usage fits within budget: `kubectl top nodes` and `kubectl top pods` — compare against Resource Budget table in spec.md (total ~578m CPU / ~1364Mi RAM requests)
- [x] T032 [P] Verify quickstart.md accuracy: walk through `specs/008-oci-oke-cloud-deployment/quickstart.md` commands and confirm they match actual deployed state
- [x] T033 [P] Clean up any `<LB_IP>` placeholder remnants in committed files — ensure no placeholders remain in `k8s/backend/values-oci.yaml` or `k8s/frontend/values-oci.yaml` (use `.gitignore` or template approach if LB_IP is dynamic)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion — BLOCKS all user stories
  - T003 (Ingress) → T004 (LB IP) → T011, T012 (values files with IP)
  - T005 (Dapr) → T014 (Dapr component)
  - T006 (Kafka manifest) → T013 (deploy Kafka)
  - T009, T010 (template mods) → T016, T017 (Helm deploy)
- **US1+US2 (Phase 3)**: Depends on Phase 2 completion (all infra + manifests ready)
- **US3 (Phase 4)**: Depends on Phase 3 (backend deployed with Dapr sidecar)
- **US4 (Phase 5)**: Depends on Phase 3 (full stack deployed to verify)
- **Polish (Phase 6)**: Depends on Phase 3+ completion

### User Story Dependencies

- **US1 + US2 (P1)**: Combined — both need full stack deployed. Start after Phase 2.
- **US3 (P2)**: Depends on US1+US2 (backend must be running with Dapr sidecar)
- **US4 (P2)**: Depends on US1+US2 (need full deployment to test operator procedures). US4 Phase 5 can run in parallel with US3 Phase 4.

### Within Phase 2 (Foundational)

```text
T003 (Ingress) ──→ T004 (LB IP) ──→ T011, T012 (values files)
T005 (Dapr)    ──→ T014 (Dapr CRD)
T006 (kafka.yaml)  ─────────────────→ T013 (deploy Kafka)
T007 (dapr-kafka-pubsub.yaml)  ──────→ T014 (deploy Dapr CRD)
T008 (ingress.yaml)  ────────────────→ T018 (apply ingress, Phase 3)
T009 (backend template) ─────────────→ T016 (deploy backend, Phase 3)
T010 (frontend template) ────────────→ T017 (deploy frontend, Phase 3)
T015 (secrets) ──────────────────────→ T016 (deploy backend, Phase 3)
```

### Parallel Opportunities

- **Phase 2 manifest creation**: T006, T007, T008 can all run in parallel (different files)
- **Phase 2 template modifications**: T009, T010 can run in parallel (different files)
- **Phase 2 values files**: T011, T012 can run in parallel (different files, both depend on T004)
- **Phase 4 + Phase 5**: US3 and US4 verification can overlap (different concerns)
- **Phase 6 polish**: T032, T033 can run in parallel (different files)

---

## Parallel Example: Phase 2 Manifest Creation

```bash
# Launch all manifest creation tasks together (different files, no dependencies):
Task: "Create k8s/kafka.yaml from contracts/kafka.yaml"           # T006
Task: "Create k8s/dapr-kafka-pubsub.yaml from contracts/"         # T007
Task: "Create k8s/ingress.yaml from contracts/ingress.yaml"       # T008
```

## Parallel Example: Phase 2 Template Modifications

```bash
# Launch both template modifications together (different files):
Task: "Add podAnnotations to k8s/backend/templates/deployment.yaml"    # T009
Task: "Add BETTER_AUTH_URL to k8s/frontend/templates/deployment.yaml"  # T010
```

---

## Implementation Strategy

### MVP First (US1 + US2 Only)

1. Complete Phase 1: Setup (T001-T002)
2. Complete Phase 2: Foundational (T003-T015)
3. Complete Phase 3: US1+US2 (T016-T022)
4. **STOP and VALIDATE**: Frontend loads, backend health 200, task CRUD works
5. Demo: `http://<LB_IP>` is live

### Incremental Delivery

1. Setup + Foundational → Infrastructure ready
2. US1+US2 (Phase 3) → App accessible via LB IP → **MVP Demo**
3. US3 (Phase 4) → Event pipeline verified → Full feature demo
4. US4 (Phase 5) → Operator procedures tested → Production-readiness demo
5. Polish (Phase 6) → Resource validation, doc accuracy

---

## Notes

- All kubectl/helm commands require active MFA session. If any command returns 401, run: `oci session authenticate --region me-dubai-1 --profile-name OKE_SESSION`
- Service names follow Helm convention `<release>-<chart>`: `todo-backend-todo-backend`, `todo-frontend-todo-frontend`
- LB IP is dynamic — changes on teardown/redeploy. All `<LB_IP>` references must be updated.
- `NEXT_PUBLIC_API_URL` is a known risk (build-time vs runtime). Test client-side API calls after deployment.
- Kafka uses Deployment (not StatefulSet) — see ADR-0008 for rationale.
- Dapr sidecar on backend only (not frontend) — see ADR-0009 for rationale.
