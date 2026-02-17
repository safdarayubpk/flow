---
id: 0004
title: Kafka Spec Review Improvements
stage: spec
date: 2026-02-10
surface: agent
model: claude-opus-4-5-20251101
feature: 006-kafka-events
branch: 006-kafka-events
user: safdarayub
command: spec review
labels: ["kafka", "spec-review", "improvements", "constitution-compliance"]
links:
  spec: specs/006-kafka-events/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/006-kafka-events/spec.md
tests:
  - null
---

## Prompt

Looking at my spec.md for phase 006-kafka-events, identify what's missing or incomplete:
(1) Are constraints explicit and comprehensive?
(2) Are non-goals clearly defined?
(3) Could someone else implement from just this spec?
(4) Does it respect project Constitution standards?

Generate 5-10 specific improvements prioritized by impact.

## Response snapshot

Identified 10 improvements and applied top 3 recommendations:

**Applied Clarifications:**
1. **Recurring Instance Scheduling**: Next 1 instance only (simplest, re-schedule after completion)
2. **Event Chaining**: Yes, publish `task-created` when Recurring Consumer creates instances
3. **File Placement**: `backend/backend/src/services/kafka/` directory

**New Sections Added:**
- **Constraints** section (6 explicit constraints)
- **Environment Variables** table (4 vars with defaults)
- **File Structure** diagram

**New Functional Requirements:**
- FR-025: Event chaining for recurring instances
- FR-026: File placement requirement
- FR-027: Docker Compose file location

**Other Updates:**
- FR-011: Updated with "next 1 instance only"
- User Story 3: Added acceptance scenario for event chaining
- Docker Compose: Specified exact image versions (Confluent 7.5.0, provectuslabs/kafka-ui)
- Clarifications: Added 3 new Q&As

## Outcome

- ✅ Impact: Spec significantly improved with 3 new sections, 4 new FRs, explicit constraints
- 🧪 Tests: N/A (specification phase)
- 📁 Files: spec.md comprehensively updated
- 🔁 Next prompts: /sp.plan
- 🧠 Reflection: Spec now self-contained for implementation; addressed constitution compliance gaps

## Evaluation notes (flywheel)

- Failure modes observed: Original spec lacked explicit constraints section, file structure, env vars
- Graders run and results (PASS/FAIL): Constitution compliance improved (constraints, file structure)
- Prompt variant (if applicable): User-requested spec review
- Next experiment (smallest change to try): N/A
