# ADR-0007: Ingress Traffic Routing and OCI Load Balancer

- **Status:** Accepted
- **Date:** 2026-02-19
- **Feature:** 008-oci-oke-cloud-deployment
- **Context:** The Flow Todo application requires external HTTP access to both a FastAPI backend and a Next.js frontend running on OKE. The backend serves endpoints at root paths (`/health`, `/tasks`) without an `/api` prefix, while users expect to access the API at `http://<IP>/api/*`. OCI requires provider-specific annotations to provision load balancers, and the cluster runs on a single free-tier node where resource efficiency matters. No DNS or TLS is available — access is IP-only over HTTP.

## Decision

- **Ingress Controller**: NGINX Ingress Controller installed via Helm (`ingress-nginx/ingress-nginx`)
- **Load Balancer**: OCI standard LB (not NLB) with flexible shape (10Mbps min/max) via annotation `oci.oraclecloud.com/load-balancer-type: lb`
- **LB Subnet**: Explicitly specified via `oci-network-load-balancer.oraclecloud.com/subnet` annotation to ensure correct network placement
- **Path Routing**: Regex-based with `rewrite-target: /$2` — `/api(/|$)(.*)` strips the `/api` prefix and forwards to backend:8000; `/(.*)` catch-all forwards to frontend:80
- **Admission Webhooks**: Disabled to save resources on the free-tier node

## Consequences

### Positive

- Single LB IP serves both frontend and backend, minimizing cost
- Regex rewrite handles the `/api` prefix stripping without backend code changes
- OCI annotations ensure predictable LB provisioning in the correct subnet
- NGINX is the most widely documented ingress controller, simplifying debugging

### Negative

- Regex rewrite rules are fragile — incorrect capture groups break routing silently
- Service names must match exactly (`todo-backend-todo-backend`, `todo-frontend-todo-frontend`) — Helm's `<release>-<chart>` naming convention is non-obvious
- No TLS termination — all traffic is plaintext HTTP
- OCI LB provisioning can be slow (2-5 minutes), adding wait time to deployment

## Alternatives Considered

- **Network Load Balancer (NLB)**: Lower cost but lacks HTTP-level features; incompatible with NGINX ingress controller's expectations for L7 routing
- **NodePort with direct node IP**: No public IP stability, requires manual firewall rule configuration in OCI security lists
- **OCI API Gateway**: Full API management but overkill for a hackathon — adds cost, complexity, and a separate service to manage
- **Host-based routing (separate subdomains)**: No DNS available; IP-only access makes host-based routing impossible
- **Path prefix without rewrite**: Would require the FastAPI backend to mount all endpoints under `/api/*`, requiring code changes across all routes
- **Separate LoadBalancer per service**: Doubles LB cost and wastes the free-tier budget

## References

- Feature Spec: [spec.md](../../specs/008-oci-oke-cloud-deployment/spec.md)
- Implementation Plan: [plan.md](../../specs/008-oci-oke-cloud-deployment/plan.md) (AD-1, AD-4)
- Research: [research.md](../../specs/008-oci-oke-cloud-deployment/research.md) (R-1, R-4)
- Contracts: [ingress.yaml](../../specs/008-oci-oke-cloud-deployment/contracts/ingress.yaml)
- Related ADRs: None
