# ADR-0010: Frontend Runtime Configuration and TLS Strategy

- **Status:** Accepted
- **Date:** 2026-02-19
- **Feature:** 008-oci-oke-cloud-deployment
- **Context:** The Next.js frontend uses `NEXT_PUBLIC_API_URL` to construct API calls. Next.js inlines `NEXT_PUBLIC_*` variables into client-side JavaScript at build time, but the OCI Load Balancer IP is only known after deployment. The Docker image was built without the correct LB IP. Additionally, a decision was needed on whether to add TLS/HTTPS for the initial deployment or defer it.

## Decision

- **NEXT_PUBLIC_API_URL**: Set as a runtime environment variable in the pod. Accept the known risk that client-side JavaScript may still reference the build-time value. Server-side rendering will use the runtime value correctly.
- **Fallback Strategy**: If client-side API calls fail, use relative URLs (`/api`) as the primary fix (works because frontend and backend share the same origin via ingress). If that's insufficient, rebuild the Docker image with `--build-arg NEXT_PUBLIC_API_URL=http://<LB_IP>/api`.
- **BETTER_AUTH_URL**: Added as a new runtime env var in the frontend deployment template (requires a small template modification).
- **TLS/HTTPS**: Deferred — no TLS for the initial deployment. HTTP-only access via IP. cert-manager + Let's Encrypt can be added later when a domain is available.

## Consequences

### Positive

- Avoids blocking the deployment on a Docker image rebuild cycle
- Relative URL fallback (`/api`) is robust because ingress ensures same-origin access
- Deferring TLS reduces deployment complexity and avoids cert-manager resource overhead
- Server-side rendering works correctly with runtime env vars

### Negative

- Client-side API calls may break if the build-time `NEXT_PUBLIC_API_URL` differs from the runtime value — requires monitoring and potential image rebuild
- No HTTPS means all traffic (including auth tokens) travels in plaintext — acceptable for hackathon demo, unacceptable for production
- `BETTER_AUTH_URL` template addition creates another divergence from the base frontend Helm chart
- Users must know to check browser console for API URL mismatches during verification

## Alternatives Considered

- **Rebuild Docker image after LB IP is known**: Guarantees correct URLs but adds a full build/push/rollout cycle to the deployment procedure
- **`publicRuntimeConfig` in next.config.js**: Deprecated in Next.js App Router — not a viable option
- **Window-level runtime injection (e.g., `__NEXT_DATA__` patching)**: Fragile and non-standard; breaks with App Router's streaming architecture
- **Self-signed TLS certificate**: Adds browser security warnings, complicates curl verification, provides marginal security benefit for a demo
- **cert-manager + Let's Encrypt**: Requires a domain name (not available), DNS configuration, and additional cluster resources — deferred to future phase

## References

- Feature Spec: [spec.md](../../specs/008-oci-oke-cloud-deployment/spec.md) (FR-009, SC-004)
- Implementation Plan: [plan.md](../../specs/008-oci-oke-cloud-deployment/plan.md) (AD-5)
- Research: [research.md](../../specs/008-oci-oke-cloud-deployment/research.md) (R-6)
- Contracts: [values-oci-frontend.yaml](../../specs/008-oci-oke-cloud-deployment/contracts/values-oci-frontend.yaml)
- Quickstart: [quickstart.md](../../specs/008-oci-oke-cloud-deployment/quickstart.md) (Known Risk section)
- Related ADRs: None
