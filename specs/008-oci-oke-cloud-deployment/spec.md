# Feature Specification: OCI OKE Cloud Deployment

**Feature Branch**: `008-oci-oke-cloud-deployment`
**Created**: 2026-02-18
**Status**: Draft
**Input**: User description: "Deploy the full Flow Todo application (FastAPI backend + Next.js frontend + Dapr pub/sub + Kafka events) to an existing OCI OKE cluster in me-dubai-1."

---

## MFA Authentication Reminder

> **Session tokens expire every ~1 hour.** Before ANY kubectl or helm command, verify your session:
>
> ```bash
> kubectl get nodes
> ```
>
> If you get `401 Unauthorized`, refresh:
>
> ```bash
> oci session authenticate --region me-dubai-1 --profile-name OKE_SESSION
> ```

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Access Todo App via Cloud URL (Priority: P1)

A user navigates to the OKE LoadBalancer IP address in their browser and sees the Flow Todo frontend. They can sign up, log in, create tasks, and interact with the application exactly as they would locally, but now hosted in the cloud on OCI infrastructure.

**Why this priority**: This is the core value of the deployment — the app must be accessible from the internet. Without this, nothing else matters.

**Independent Test**: Can be fully tested by opening `http://<LB_IP>` in a browser, signing up, creating a task, and verifying it persists.

**Acceptance Scenarios**:

1. **Given** all pods are running in OKE, **When** a user navigates to `http://<LB_IP>`, **Then** the Next.js frontend loads successfully
2. **Given** the frontend is accessible, **When** a user creates an account and logs in, **Then** authentication completes successfully via Better Auth
3. **Given** the user is logged in, **When** they create a new task with title, priority, and tags, **Then** the task is saved to the database and appears in the dashboard

---

### User Story 2 - Backend API Health and Routing (Priority: P1)

The backend API is accessible through the ingress at `/api/*` paths. Health checks return 200 OK, and all CRUD operations for tasks work correctly through the ingress routing.

**Why this priority**: The backend API is the data backbone — the frontend depends on it for all operations.

**Independent Test**: Can be tested by running `curl http://<LB_IP>/api/health` and verifying a 200 response.

**Acceptance Scenarios**:

1. **Given** the backend pod is running with Dapr sidecar, **When** a request hits `http://<LB_IP>/api/health`, **Then** the backend returns HTTP 200
2. **Given** the ingress is configured, **When** a request to `/api/tasks` is made with valid auth, **Then** the backend returns the user's tasks
3. **Given** the backend is connected to Neon PostgreSQL, **When** a task is created, **Then** it is persisted in the external database

---

### User Story 3 - Event-Driven Task Processing via Dapr and Kafka (Priority: P2)

When a user creates, updates, or completes a task, the backend publishes an event through Dapr pub/sub to Kafka. The event pipeline works end-to-end within the Kubernetes cluster.

**Why this priority**: Event-driven architecture is important for the full application experience but the app remains functional for basic CRUD without it.

**Independent Test**: Can be tested by creating a task and checking backend logs for successful Dapr pub/sub event publishing.

**Acceptance Scenarios**:

1. **Given** Kafka and Dapr are running in the cluster, **When** a task is created, **Then** a task-event is published to the `task-events` topic via Dapr pub/sub
2. **Given** the Dapr sidecar is injected into the backend pod, **When** the backend starts, **Then** it connects to the Dapr sidecar without errors
3. **Given** Kafka broker is running, **When** checking Kafka topics, **Then** the `task-events` topic exists

---

### User Story 4 - Operator Deploys and Manages the Stack (Priority: P2)

A developer or operator can deploy the entire stack using documented copy-paste Helm and kubectl commands. They can verify deployment status, troubleshoot issues, refresh MFA sessions, and tear down/redeploy when needed.

**Why this priority**: Repeatable deployment is essential for maintenance and recovery, but this is an operator concern rather than end-user value.

**Independent Test**: Can be tested by following the deployment procedure from scratch and verifying all components come up healthy.

**Acceptance Scenarios**:

1. **Given** an authenticated kubectl session, **When** the operator follows the deployment steps in order, **Then** all components deploy without errors
2. **Given** the MFA session has expired, **When** the operator runs the session refresh command, **Then** kubectl operations resume working
3. **Given** all components are deployed, **When** the operator runs verification commands, **Then** all pods show Running, services have correct ports, and ingress has an assigned IP
4. **Given** a deployment has failed, **When** the operator runs the teardown procedure, **Then** all components are removed and a fresh deployment can be performed

---

### Edge Cases

- What happens when the OCI MFA session token expires mid-deployment? Deployment commands fail with 401; operator must refresh the session and retry the failed step.
- What happens when Kafka is not yet ready but the backend starts? The backend starts and serves CRUD normally; event publishing silently fails with log warnings. Task CRUD is never blocked by Kafka/Dapr availability.
- What happens when the single node runs out of memory (8GB limit)? Pods enter OOMKilled or Pending state. Resource requests/limits must be tuned to fit all components within the 8GB budget.
- What happens when the Neon PostgreSQL external database is unreachable? Backend health check fails, API returns errors, but the cluster itself remains healthy.
- What happens when the LoadBalancer IP is not yet assigned? Frontend and backend are accessible only within the cluster. The operator must wait for OCI to provision the LB before configuring URLs.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST route HTTP requests at `/api/*` to the backend service and all other paths to the frontend service via an ingress controller
- **FR-002**: System MUST provision an OCI Load Balancer with a public IP address for external access to the application
- **FR-003**: System MUST run Dapr sidecars alongside the backend pod only for pub/sub and service invocation capabilities; the frontend pod does NOT require a Dapr sidecar
- **FR-004**: System MUST run a Kafka broker within the cluster accessible to the Dapr pub/sub component
- **FR-005**: System MUST store sensitive configuration (database URLs, API keys, auth secrets) as Kubernetes Secrets, never committed to the repository
- **FR-006**: System MUST use existing Helm charts from `k8s/backend/` and `k8s/frontend/` with environment-specific value overrides (minimal template changes allowed only for `podAnnotations` support)
- **FR-007**: System MUST fit all components (ingress, Dapr, Kafka, Zookeeper, backend, frontend) within the resource budget of a single VM.Standard.E2.1 node (1 OCPU, 8GB RAM)
- **FR-008**: System MUST persist Kafka data using a persistent volume to survive pod restarts
- **FR-009**: System MUST support MFA-authenticated kubectl operations using session tokens
- **FR-010**: System MUST provide a documented, sequential deployment procedure with copy-paste commands
- **FR-011**: System MUST provide verification commands to confirm successful deployment of each component
- **FR-012**: System MUST configure the backend with correct CORS origins matching the LoadBalancer IP
- **FR-013**: System MUST configure the frontend with the correct API URL and auth URL pointing to the LoadBalancer IP
- **FR-014**: System MUST provide a clean-slate teardown procedure to remove all deployed components, enabling full redeployment from step 1 on failure

### Key Entities

- **Ingress Controller**: Routes external HTTP traffic to backend and frontend services based on URL path patterns
- **Dapr Sidecar**: Per-pod process that provides pub/sub messaging and service invocation abstraction
- **Kafka Broker**: Single-node message broker that stores and delivers events for the task-events topic
- **Kubernetes Secret**: Cluster-stored encrypted configuration containing database URLs, API keys, and auth secrets
- **Helm Values Override**: Environment-specific configuration file (`values-oci.yaml`) that adapts the existing charts for OCI deployment
- **OCI Load Balancer**: Cloud-provisioned network load balancer that provides a public IP for ingress traffic

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All application pods (backend, frontend, Kafka, Zookeeper, Dapr, ingress) reach Running state within the cluster
- **SC-002**: The frontend loads successfully when accessing the LoadBalancer public IP via a browser
- **SC-003**: The backend health endpoint returns HTTP 200 when accessed via `http://<LB_IP>/api/health`
- **SC-004**: A user can complete the full task lifecycle (create, read, update, complete, delete) through the cloud-hosted application
- **SC-005**: Task events are published to Kafka via Dapr when tasks are created or modified, confirmed via backend logs
- **SC-006**: Total cluster resource usage fits within the single node's capacity (1 OCPU, 8GB RAM) with all components running
- **SC-007**: The entire deployment can be completed by following the documented step-by-step commands without undocumented troubleshooting
- **SC-008**: After an MFA session refresh, all kubectl operations resume without redeployment

## Clarifications

### Session 2026-02-18

- Q: What should happen if Dapr or Kafka is permanently unavailable during the backend pod lifecycle? → A: Backend starts and serves CRUD normally; event publishing silently fails with log warnings. Task CRUD is never blocked by Kafka/Dapr availability.
- Q: If a deployment step fails partway through, what is the expected recovery approach? → A: Clean-slate: provide a single teardown command list to remove everything, then redeploy from step 1.
- Q: Should the frontend pod also receive a Dapr sidecar? → A: No. Frontend communicates via ingress HTTP only; no Dapr sidecar needed. Saves ~64Mi RAM on the constrained node.

## Assumptions

- OKE cluster `todo-oke-cluster` in me-dubai-1 is ACTIVE with 1x VM.Standard.E2.1 node
- kubectl is authenticated via MFA security_token and `~/.oci/oke-token.sh` wrapper
- Docker images `safdarayub/todo-backend:v3-complete` and `safdarayub/todo-frontend:v3-complete` are publicly available on Docker Hub
- Neon PostgreSQL is externally accessible and requires no in-cluster database deployment
- Helm charts at `k8s/backend/` and `k8s/frontend/` are functional and need value overrides for OCI plus a minimal `podAnnotations` template addition for Dapr
- No TLS/HTTPS is required for initial deployment (HTTP-only access via IP)
- No CI/CD pipeline; all deployments are manual via CLI
- Single namespace (`default`) is used for all components
- No custom DNS; access is via raw LoadBalancer IP address

## Non-Goals

- No CI/CD pipeline setup
- No TLS/HTTPS or cert-manager configuration
- No custom domain or DNS setup
- No Horizontal Pod Autoscaler
- No OCI Vault or advanced secret rotation
- No Terraform or infrastructure-as-code
- No multi-environment or multi-namespace support
- No advanced monitoring, alerting, or observability stack

## Dependencies

- **External**: Neon PostgreSQL database (existing, accessed via DATABASE_URL)
- **External**: Docker Hub (public images, no pull secret needed)
- **External**: OCI Load Balancer service (provisioned by OCI when ingress is created)
- **Internal**: Existing Helm charts at `k8s/backend/` and `k8s/frontend/`
- **Internal**: OCI MFA session token (expires ~1 hour, must be refreshed)

---

## Deployment Order (Step-by-Step)

> **Before every step**: If kubectl returns `401 Unauthorized`, refresh MFA:
> `oci session authenticate --region me-dubai-1 --profile-name OKE_SESSION`

### Step 0: Verify Cluster Access

```bash
kubectl get nodes
# Expected: 1 node in Ready state
```

### Step 1: Add Helm Repos

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo add dapr https://dapr.github.io/helm-charts
helm repo update
```

### Step 2: Install NGINX Ingress Controller

```bash
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx --create-namespace \
  --set controller.service.annotations."oci\.oraclecloud\.com/load-balancer-type"="lb" \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/oci-load-balancer-shape"="flexible" \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/oci-load-balancer-shape-flex-min"="10" \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/oci-load-balancer-shape-flex-max"="10" \
  --set controller.service.annotations."oci-network-load-balancer\.oraclecloud\.com/subnet"="ocid1.subnet.oc1.me-dubai-1.aaaaaaaasbvbt52uox37vywgrqmv3pawnznopr43syql5z6qviepthuk7qua" \
  --set controller.resources.requests.cpu=50m \
  --set controller.resources.requests.memory=64Mi \
  --set controller.resources.limits.cpu=200m \
  --set controller.resources.limits.memory=128Mi \
  --set controller.admissionWebhooks.enabled=false
```

### Step 3: Wait for LoadBalancer IP

```bash
kubectl get svc -n ingress-nginx ingress-nginx-controller -w
# Wait until EXTERNAL-IP changes from <pending> to an actual IP
# Press Ctrl+C once IP appears, then note the IP:
export LB_IP=$(kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "LoadBalancer IP: $LB_IP"
```

### Step 4: Install Dapr

```bash
helm install dapr dapr/dapr \
  --namespace dapr-system --create-namespace \
  --set global.logAsJson=true \
  --set dapr_sidecar_injector.resources.requests.cpu=10m \
  --set dapr_sidecar_injector.resources.requests.memory=32Mi \
  --set dapr_sidecar_injector.resources.limits.cpu=100m \
  --set dapr_sidecar_injector.resources.limits.memory=64Mi \
  --set dapr_operator.resources.requests.cpu=10m \
  --set dapr_operator.resources.requests.memory=32Mi \
  --set dapr_operator.resources.limits.cpu=100m \
  --set dapr_operator.resources.limits.memory=64Mi \
  --set dapr_placement.resources.requests.cpu=10m \
  --set dapr_placement.resources.requests.memory=32Mi \
  --set dapr_placement.resources.limits.cpu=100m \
  --set dapr_placement.resources.limits.memory=64Mi \
  --set dapr_sentry.resources.requests.cpu=10m \
  --set dapr_sentry.resources.requests.memory=32Mi \
  --set dapr_sentry.resources.limits.cpu=100m \
  --set dapr_sentry.resources.limits.memory=64Mi

# Verify Dapr is running:
kubectl get pods -n dapr-system
```

### Step 5: Deploy Kafka + Zookeeper

Apply the Kafka manifest at `k8s/kafka.yaml`:

```yaml
# k8s/kafka.yaml
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: kafka-data
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: oci-bv
  resources:
    requests:
      storage: 5Gi
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: zookeeper
  labels:
    app: zookeeper
spec:
  replicas: 1
  selector:
    matchLabels:
      app: zookeeper
  template:
    metadata:
      labels:
        app: zookeeper
    spec:
      containers:
        - name: zookeeper
          image: confluentinc/cp-zookeeper:7.5.0
          ports:
            - containerPort: 2181
          env:
            - name: ZOOKEEPER_CLIENT_PORT
              value: "2181"
            - name: ZOOKEEPER_TICK_TIME
              value: "2000"
          resources:
            requests:
              cpu: 50m
              memory: 128Mi
            limits:
              cpu: 200m
              memory: 256Mi
---
apiVersion: v1
kind: Service
metadata:
  name: zookeeper
spec:
  selector:
    app: zookeeper
  ports:
    - port: 2181
      targetPort: 2181
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kafka
  labels:
    app: kafka
spec:
  replicas: 1
  selector:
    matchLabels:
      app: kafka
  template:
    metadata:
      labels:
        app: kafka
    spec:
      containers:
        - name: kafka
          image: confluentinc/cp-kafka:7.5.0
          ports:
            - containerPort: 9092
          env:
            - name: KAFKA_BROKER_ID
              value: "1"
            - name: KAFKA_ZOOKEEPER_CONNECT
              value: "zookeeper:2181"
            - name: KAFKA_LISTENER_SECURITY_PROTOCOL_MAP
              value: "PLAINTEXT:PLAINTEXT"
            - name: KAFKA_ADVERTISED_LISTENERS
              value: "PLAINTEXT://kafka:9092"
            - name: KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR
              value: "1"
            - name: KAFKA_AUTO_CREATE_TOPICS_ENABLE
              value: "true"
          resources:
            requests:
              cpu: 100m
              memory: 256Mi
            limits:
              cpu: 500m
              memory: 512Mi
          volumeMounts:
            - name: kafka-data
              mountPath: /var/lib/kafka/data
      volumes:
        - name: kafka-data
          persistentVolumeClaim:
            claimName: kafka-data
---
apiVersion: v1
kind: Service
metadata:
  name: kafka
spec:
  selector:
    app: kafka
  ports:
    - port: 9092
      targetPort: 9092
```

```bash
kubectl apply -f k8s/kafka.yaml

# Wait for pods:
kubectl wait --for=condition=ready pod -l app=zookeeper --timeout=120s
kubectl wait --for=condition=ready pod -l app=kafka --timeout=120s
```

### Step 6: Deploy Dapr Pub/Sub Component

Apply the Dapr component at `k8s/dapr-kafka-pubsub.yaml`:

```yaml
# k8s/dapr-kafka-pubsub.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "kafka.default.svc.cluster.local:9092"
    - name: consumerGroup
      value: "dapr-todo-backend"
    - name: authRequired
      value: "false"
    - name: maxMessageBytes
      value: "1048576"
```

```bash
kubectl apply -f k8s/dapr-kafka-pubsub.yaml
```

### Step 7: Create Kubernetes Secrets

```bash
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL='<YOUR_NEON_DATABASE_URL>' \
  --from-literal=SECRET_KEY='<YOUR_SECRET_KEY>' \
  --from-literal=BETTER_AUTH_SECRET='<YOUR_BETTER_AUTH_SECRET>' \
  --from-literal=GROQ_API_KEY='<YOUR_GROQ_API_KEY>' \
  --from-literal=OPENAI_API_KEY='<YOUR_OPENAI_API_KEY>'

# Verify:
kubectl get secret todo-secrets
```

> **Never commit actual secret values to the repository.** Replace `<YOUR_*>` placeholders with real values from your `.env` file.

### Step 8: Create values-oci.yaml for Backend

Create `k8s/backend/values-oci.yaml`:

```yaml
# k8s/backend/values-oci.yaml
# OCI OKE deployment overrides for todo-backend

image:
  repository: safdarayub/todo-backend
  tag: v3-complete
  pullPolicy: Always

resources:
  requests:
    cpu: 64m
    memory: 128Mi
  limits:
    cpu: 250m
    memory: 384Mi

env:
  LOG_LEVEL: "INFO"
  CORS_ORIGINS: "http://<LB_IP>"

# Dapr sidecar injection
podAnnotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "todo-backend"
  dapr.io/app-port: "8000"
  dapr.io/log-level: "warn"
  dapr.io/sidecar-cpu-request: "10m"
  dapr.io/sidecar-memory-request: "32Mi"
  dapr.io/sidecar-cpu-limit: "100m"
  dapr.io/sidecar-memory-limit: "64Mi"
```

> **Note**: The backend Helm template needs a small addition to support `podAnnotations`. Add to `k8s/backend/templates/deployment.yaml` under `spec.template.metadata`:
> ```yaml
>       {{- with .Values.podAnnotations }}
>       annotations:
>         {{- toYaml . | nindent 8 }}
>       {{- end }}
> ```

### Step 9: Create values-oci.yaml for Frontend

Create `k8s/frontend/values-oci.yaml`:

```yaml
# k8s/frontend/values-oci.yaml
# OCI OKE deployment overrides for todo-frontend

image:
  repository: safdarayub/todo-frontend
  tag: v3-complete
  pullPolicy: Always

resources:
  requests:
    cpu: 64m
    memory: 128Mi
  limits:
    cpu: 250m
    memory: 384Mi

env:
  LOG_LEVEL: "INFO"
  NEXT_PUBLIC_API_URL: "http://<LB_IP>/api"
  BETTER_AUTH_URL: "http://<LB_IP>"
```

> **Note**: The frontend Helm template needs a small addition to support `BETTER_AUTH_URL`. Add to `k8s/frontend/templates/deployment.yaml` under `env:`:
> ```yaml
>           {{- if .Values.env.BETTER_AUTH_URL }}
>             - name: BETTER_AUTH_URL
>               value: {{ .Values.env.BETTER_AUTH_URL | quote }}
>           {{- end }}
> ```

### Step 10: Deploy Backend

```bash
# Replace <LB_IP> in values-oci.yaml first, then:
helm upgrade --install todo-backend ./k8s/backend \
  --values k8s/backend/values-oci.yaml

# Verify:
kubectl get pods -l app.kubernetes.io/name=todo-backend
kubectl logs -l app.kubernetes.io/name=todo-backend --tail=20
```

### Step 11: Deploy Frontend

```bash
# Replace <LB_IP> in values-oci.yaml first, then:
helm upgrade --install todo-frontend ./k8s/frontend \
  --values k8s/frontend/values-oci.yaml

# Verify:
kubectl get pods -l app.kubernetes.io/name=todo-frontend
```

### Step 12: Apply Ingress Resource

Apply the Ingress at `k8s/ingress.yaml`:

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: todo-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /$2
    nginx.ingress.kubernetes.io/use-regex: "true"
spec:
  ingressClassName: nginx
  rules:
    - http:
        paths:
          - path: /api(/|$)(.*)
            pathType: ImplementationSpecific
            backend:
              service:
                name: todo-backend-todo-backend
                port:
                  number: 8000
          - path: /(.*)
            pathType: ImplementationSpecific
            backend:
              service:
                name: todo-frontend-todo-frontend
                port:
                  number: 80
```

```bash
kubectl apply -f k8s/ingress.yaml

# Verify:
kubectl get ingress todo-ingress
```

> **Service names**: The Helm-generated service names follow the pattern `<release>-<chart>`. With `helm install todo-backend ./k8s/backend`, the service name is `todo-backend-todo-backend`. Verify with `kubectl get svc` and adjust the Ingress if needed.

### Step 13: Verify End-to-End

```bash
# All pods running:
kubectl get pods

# Services:
kubectl get svc

# Ingress:
kubectl get ingress

# Backend health:
curl http://$LB_IP/api/health

# Frontend loads:
curl -s http://$LB_IP | head -20

# Backend logs (check for Dapr/Kafka errors):
kubectl logs -l app.kubernetes.io/name=todo-backend -c todo-backend --tail=50
```

---

## Teardown Procedure

To remove all deployed components for a clean-slate redeployment:

```bash
# 1. Remove application components
kubectl delete ingress todo-ingress 2>/dev/null
helm uninstall todo-frontend 2>/dev/null
helm uninstall todo-backend 2>/dev/null
kubectl delete secret todo-secrets 2>/dev/null

# 2. Remove Dapr component and Kafka
kubectl delete -f k8s/dapr-kafka-pubsub.yaml 2>/dev/null
kubectl delete -f k8s/kafka.yaml 2>/dev/null
kubectl delete pvc kafka-data 2>/dev/null

# 3. Remove Dapr runtime
helm uninstall dapr -n dapr-system 2>/dev/null
kubectl delete namespace dapr-system 2>/dev/null

# 4. Remove Ingress Controller (also deletes the OCI Load Balancer)
helm uninstall ingress-nginx -n ingress-nginx 2>/dev/null
kubectl delete namespace ingress-nginx 2>/dev/null

# 5. Verify clean state
kubectl get pods
kubectl get svc
kubectl get pvc
```

> **Warning**: Step 4 deletes the OCI Load Balancer, which means a new public IP will be assigned on redeployment. You will need to update all `<LB_IP>` references in values-oci.yaml files.

---

## Resource Budget

All components must fit within the single-node constraint (1 OCPU / 1000m, 8GB RAM):

| Component              | CPU Request | CPU Limit | RAM Request | RAM Limit |
| ---------------------- | ----------- | --------- | ----------- | --------- |
| Backend                | 64m         | 250m      | 128Mi       | 384Mi     |
| Backend Dapr sidecar   | 10m         | 100m      | 32Mi        | 64Mi      |
| Frontend               | 64m         | 250m      | 128Mi       | 384Mi     |
| Kafka                  | 100m        | 500m      | 256Mi       | 512Mi     |
| Zookeeper              | 50m         | 200m      | 128Mi       | 256Mi     |
| Dapr system (4 pods)   | 40m         | 400m      | 128Mi       | 256Mi     |
| Ingress controller     | 50m         | 200m      | 64Mi        | 128Mi     |
| **App Total**          | **378m**    | **1900m** | **864Mi**   | **1984Mi** |
| K8s system (reserved)  | ~200m       | —         | ~500Mi      | —         |
| **Grand Total**        | **~578m**   | —         | **~1364Mi** | —         |

Remaining headroom: ~422m CPU request, ~6.6GB RAM (limits can burst up to node capacity). The system is request-constrained, not limit-constrained, which is safe for a single-node hackathon setup.

---

## OCI Infrastructure Reference

| Resource          | Value |
| ----------------- | ----- |
| Region            | me-dubai-1 |
| Cluster           | todo-oke-cluster |
| Cluster OCID      | `ocid1.cluster.oc1.me-dubai-1.aaaaaaaag2nmeu5aworqfjb7bussqszpnvo3kp4tqlms5sj3sciwo4wljedq` |
| Node Shape        | VM.Standard.E2.1 (1 OCPU, 8GB RAM, x86) |
| LB Subnet OCID    | `ocid1.subnet.oc1.me-dubai-1.aaaaaaaasbvbt52uox37vywgrqmv3pawnznopr43syql5z6qviepthuk7qua` |
| Node Subnet OCID  | `ocid1.subnet.oc1.me-dubai-1.aaaaaaaaz2wh7mnyxszwt46u5cyl4s46626on7oypa2zooi6rnn3curtlexa` |
| API Endpoint      | `https://139.185.40.234:6443` |
| MFA Auth Profile  | `OKE_SESSION` (security_token auth) |
| Token Wrapper     | `~/.oci/oke-token.sh` (converts v1beta1 → v1 for kubectl v1.35+) |

## Template Changes Required

The existing Helm chart templates need two minimal additions to support OCI deployment:

1. **Backend `deployment.yaml`**: Add `podAnnotations` support for Dapr sidecar injection
2. **Frontend `deployment.yaml`**: Add `BETTER_AUTH_URL` environment variable support

These are single-block additions to existing templates, not rewrites. The values-oci.yaml override pattern is preserved.
