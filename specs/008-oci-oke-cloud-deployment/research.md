# Research: OCI OKE Cloud Deployment

**Feature**: 008-oci-oke-cloud-deployment
**Date**: 2026-02-19

## R-1: OCI Load Balancer Annotations for NGINX Ingress

**Decision**: Use `oci.oraclecloud.com/load-balancer-type: lb` with flexible shape annotations.

**Rationale**: OCI requires specific service annotations to provision load balancers. The flexible shape (10Mbps) is the most cost-effective for free-tier. The LB subnet OCID must be explicitly specified to ensure placement in the correct network.

**Alternatives considered**:
- Network Load Balancer (`nlb`) — lower cost but no HTTP-level features, incompatible with NGINX ingress controller expectations
- NodePort with direct node IP — no public IP stability, requires firewall rules
- OCI API Gateway — overkill for a hackathon project, adds cost and complexity

## R-2: Kafka Deployment Strategy on Free-Tier OKE

**Decision**: Use simple Kubernetes Deployments (not StatefulSet, not Strimzi) for Kafka and Zookeeper with a PVC for data persistence.

**Rationale**: A single-broker, single-Zookeeper setup doesn't benefit from StatefulSet features (stable network identity, ordered scaling). A Deployment with a PVC is simpler, easier to debug, and sufficient for a hackathon demo. Confluent `cp-kafka:7.5.0` and `cp-zookeeper:7.5.0` images are x86/amd64, matching the node architecture.

**Alternatives considered**:
- Strimzi Operator — too heavy for free-tier (operator alone uses ~256Mi RAM), designed for production multi-broker clusters
- StatefulSet — adds unnecessary complexity for 1-replica setup; no benefit over Deployment+PVC
- Redpanda — lighter than Kafka but introduces a new technology not used in prior phases
- KRaft mode (no Zookeeper) — requires Kafka 3.6+ with KRaft GA; cp-kafka:7.5.0 supports it but adds config complexity

## R-3: Dapr on Kubernetes Installation

**Decision**: Install Dapr via official Helm chart (`dapr/dapr`) with aggressive resource limits to fit free-tier node.

**Rationale**: Dapr Helm chart is the standard K8s installation method. Default resource requests are too high for free-tier (~128Mi per component × 4 = 512Mi). Overriding to 32Mi per component (4 × 32Mi = 128Mi total) is viable for low-traffic hackathon usage.

**Alternatives considered**:
- Dapr CLI `dapr init -k` — installs with defaults, no resource customization
- Skip Dapr entirely — would break the Dapr pub/sub feature from Phase V.3
- Dapr Standalone mode — not applicable to K8s deployment

## R-4: Ingress Rewrite Rules for Dual-Service Routing

**Decision**: Use NGINX `rewrite-target: /$2` with regex capture groups to route `/api/*` to backend and `/*` to frontend.

**Rationale**: The backend FastAPI app serves endpoints at `/health`, `/tasks`, etc. (without `/api` prefix). The frontend expects to be served at root `/`. The ingress must strip `/api` when forwarding to the backend. NGINX ingress controller's regex rewrite is the standard approach.

**Alternatives considered**:
- Host-based routing (separate subdomains) — no DNS, IP-only access
- Path prefix without rewrite — would require backend to mount at `/api/*` (code change)
- Separate LoadBalancer per service — doubles cost and complexity

## R-5: OCI Block Volume StorageClass

**Decision**: Use `oci-bv` StorageClass for Kafka PVC.

**Rationale**: `oci-bv` is the default OCI Block Volume StorageClass available in all OKE clusters. It provisions iSCSI-attached block volumes. The minimum size for OCI Block Volumes is 50Gi in the console, but the API/PVC can request smaller (5Gi). Performance is sufficient for a single-broker hackathon Kafka setup.

**Alternatives considered**:
- `oci-bv-encrypted` — adds encryption overhead, unnecessary for hackathon
- emptyDir — data lost on pod restart, violates FR-008
- hostPath — ties to specific node, problematic for rescheduling

## R-6: NEXT_PUBLIC_API_URL Build-Time vs Runtime

**Decision**: Set `NEXT_PUBLIC_API_URL` as a runtime env var in the pod and accept the risk that client-side code may not pick it up. Document the fallback of rebuilding the Docker image.

**Rationale**: Next.js `NEXT_PUBLIC_*` vars are inlined into client-side JavaScript at build time. However, Next.js 13+ with standalone output does support runtime env vars for server-side rendering. The server components and API routes will use the runtime value. Client-side `fetch` calls that use `NEXT_PUBLIC_API_URL` may still reference the build-time value. If this causes issues, the image needs rebuilding with `--build-arg NEXT_PUBLIC_API_URL=http://<LB_IP>/api`.

**Alternatives considered**:
- Rebuild Docker image after LB IP is known — guaranteed correct but adds a deployment step
- Use relative URLs (`/api`) — would work if frontend and backend share the same origin (which they do via ingress), making this the best fallback
- Runtime config via `next.config.js` `publicRuntimeConfig` — deprecated in App Router
