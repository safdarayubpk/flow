---
name: oci-oke-expert
description: >
  OCI & OKE specialist for the Todo app hackathon project. Provides infrastructure context,
  authentication patterns, and deployment guidance for Oracle Kubernetes Engine in me-dubai-1.
  Use when working with: OKE cluster operations, kubectl commands, oci CLI, Helm deploys to OKE,
  Dapr/Kafka on OKE, Ingress/LoadBalancer setup, Kubernetes secrets, cloud deployment,
  OCI networking, node pool management, or troubleshooting OKE auth errors.
  Triggers: "OKE", "oci", "kubectl", "deploy to cloud", "cluster", "OCI", "oracle kubernetes",
  "ingress on OKE", "secrets on OKE", "Dapr on OKE", "Kafka on OKE", "node pool", "DOKS alternative".
---

# OCI OKE Expert

## Essential Context

- **Region:** me-dubai-1 — **Cluster:** todo-oke-cluster (v1.32.1, BASIC_CLUSTER)
- **Node:** 1x VM.Standard.E2.1 (x86, 8GB) — images are amd64, never use ARM without rebuild
- **MFA enabled:** Always use `--auth security_token --profile OKE_SESSION` for OKE/token commands
- **Auth wrapper:** `~/.oci/oke-token.sh` converts v1beta1→v1 exec API for kubectl v1.35+
- **Session expires ~1hr.** On 401: `oci session authenticate --region me-dubai-1 --profile-name OKE_SESSION`
- **Images:** `safdarayub/todo-backend:v3-complete`, `safdarayub/todo-frontend:v3-complete` (Docker Hub, public)
- **Helm charts:** `k8s/backend/`, `k8s/frontend/` — values already point to v3-complete images

## Constraints

- Prefer Always Free tier. Single cluster, single namespace, no CI/CD, IP-based access only.
- All steps as copy-paste commands. Beginner-friendly.

## References

- **OCIDs & networking details:** See [references/infrastructure.md](references/infrastructure.md)
- **Troubleshooting:** See [references/troubleshooting.md](references/troubleshooting.md)
