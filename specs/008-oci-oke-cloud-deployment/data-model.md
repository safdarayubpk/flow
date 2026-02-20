# Data Model: OCI OKE Cloud Deployment

**Feature**: 008-oci-oke-cloud-deployment
**Date**: 2026-02-19

This feature deploys existing application code — no new data entities are created. The data model below describes the **deployment topology** (Kubernetes resources and their relationships).

## Deployment Topology

### Namespaces

| Namespace       | Components                                    |
| --------------- | --------------------------------------------- |
| `default`       | Backend, Frontend, Kafka, Zookeeper, Ingress, Dapr Component, Secrets |
| `ingress-nginx` | NGINX Ingress Controller                      |
| `dapr-system`   | Dapr Operator, Sidecar Injector, Placement, Sentry |

### Resource Inventory

| Resource Type    | Name                        | Namespace       | Source         |
| ---------------- | --------------------------- | --------------- | -------------- |
| Deployment       | todo-backend-todo-backend   | default         | Helm chart     |
| Deployment       | todo-frontend-todo-frontend | default         | Helm chart     |
| Deployment       | kafka                       | default         | k8s/kafka.yaml |
| Deployment       | zookeeper                   | default         | k8s/kafka.yaml |
| Service          | todo-backend-todo-backend   | default         | Helm chart     |
| Service          | todo-frontend-todo-frontend | default         | Helm chart     |
| Service          | kafka                       | default         | k8s/kafka.yaml |
| Service          | zookeeper                   | default         | k8s/kafka.yaml |
| Ingress          | todo-ingress                | default         | k8s/ingress.yaml |
| PVC              | kafka-data                  | default         | k8s/kafka.yaml |
| Secret           | todo-secrets                | default         | kubectl create |
| Dapr Component   | kafka-pubsub                | default         | k8s/dapr-kafka-pubsub.yaml |
| Helm Release     | ingress-nginx               | ingress-nginx   | Helm install   |
| Helm Release     | dapr                        | dapr-system     | Helm install   |

### Network Topology

```text
Internet
  │
  ▼
OCI Load Balancer (public IP, LB subnet)
  │
  ▼
NGINX Ingress Controller (ingress-nginx namespace)
  │
  ├── /api/* ──→ todo-backend-todo-backend:8000 (default)
  │                    │
  │                    ├── Dapr Sidecar ──→ kafka-pubsub Component
  │                    │                         │
  │                    │                         ▼
  │                    │                    kafka:9092 ◄── zookeeper:2181
  │                    │
  │                    └── Neon PostgreSQL (external, via DATABASE_URL)
  │
  └── /* ──→ todo-frontend-todo-frontend:80 (default)
                   │
                   └── Server-side: NEXT_PUBLIC_API_URL → http://<LB_IP>/api
```

### Secret Keys

| Key                | Source              | Used By    |
| ------------------ | ------------------- | ---------- |
| DATABASE_URL       | Neon PostgreSQL URL | Backend    |
| SECRET_KEY         | App signing key     | Backend    |
| BETTER_AUTH_SECRET | Auth session key    | Backend    |
| GROQ_API_KEY       | Groq API (optional) | Backend    |
| OPENAI_API_KEY     | OpenAI (optional)   | Backend    |

### Environment Variables (via values-oci.yaml)

| Variable            | Value                    | Set In    |
| ------------------- | ------------------------ | --------- |
| CORS_ORIGINS        | `http://<LB_IP>`         | Backend   |
| LOG_LEVEL           | `INFO`                   | Both      |
| NEXT_PUBLIC_API_URL | `http://<LB_IP>/api`     | Frontend  |
| BETTER_AUTH_URL     | `http://<LB_IP>`         | Frontend  |

## State Transitions

No new state machines. The existing task lifecycle (created → updated → completed → deleted) is unchanged. Kafka events are fire-and-forget with graceful degradation.

## Data Persistence

| Data              | Storage                | Persistence  |
| ----------------- | ---------------------- | ------------ |
| Application data  | Neon PostgreSQL        | External, persistent |
| Kafka events      | OCI Block Volume (5Gi) | Persistent across pod restarts |
| Next.js cache     | emptyDir               | Ephemeral (lost on restart) |
| Temp files        | emptyDir               | Ephemeral (lost on restart) |
