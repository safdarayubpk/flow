---
id: "0010"
title: OCI OKE Cloud Deployment Spec
stage: spec
date: 2026-02-18
surface: agent
model: claude-opus-4-6
feature: 008-oci-oke-cloud-deployment
branch: 008-oci-oke-cloud-deployment
user: safdarayub
command: /sp.specify
labels: ["oci", "oke", "cloud-deployment", "kubernetes", "spec"]
links:
  spec: specs/008-oci-oke-cloud-deployment/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/008-oci-oke-cloud-deployment/spec.md
  - specs/008-oci-oke-cloud-deployment/checklists/requirements.md
tests:
  - Spec quality checklist validation (all items passed)
---

## Prompt

Phase V.4: OCI OKE Cloud Deployment

Feature: 008-oci-oke-cloud-deployment

Deploy the full Flow Todo application (FastAPI backend + Next.js frontend + Dapr pub/sub + Kafka events) to an existing OCI OKE cluster in me-dubai-1.

Requirements include: NGINX Ingress Controller with OCI LB annotations, Dapr on Kubernetes with sidecar injection, simple Kafka StatefulSet with Zookeeper, Kubernetes Secrets management, Helm values overrides for OCI, documented step-by-step deployment order, and verification steps.

Constraints: Must work with existing Helm charts, free-tier friendly (1x VM.Standard.E2.1, 1 OCPU, 8GB RAM), beginner-friendly copy-paste commands, me-dubai-1 region, MFA authentication.

## Response snapshot

Generated feature specification at `specs/008-oci-oke-cloud-deployment/spec.md` with:
- 4 user stories (2x P1: frontend access + backend API; 2x P2: Dapr/Kafka events + operator deployment)
- 13 functional requirements covering ingress routing, LB provisioning, Dapr sidecars, Kafka, secrets, Helm overrides, resource budget, MFA auth, and deployment docs
- 8 success criteria (all measurable, technology-agnostic)
- 5 edge cases (MFA expiry, Kafka readiness, OOM, DB unreachable, LB pending)
- Resource budget table fitting all components within 8GB RAM / 1 OCPU
- 13-step deployment order
- Quality checklist: all items passed

Created branch `008-oci-oke-cloud-deployment` and quality checklist at `specs/008-oci-oke-cloud-deployment/checklists/requirements.md`.

## Outcome

- Impact: Feature specification complete and validated, ready for /sp.plan
- Tests: Quality checklist passed all items
- Files: spec.md + checklists/requirements.md created
- Next prompts: /sp.plan or /sp.clarify for implementation planning
- Reflection: Spec is comprehensive but stays technology-agnostic at the right level. Resource budget table is borderline implementation detail but necessary as it defines the constraint boundary.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Quality checklist PASS (all items checked)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
