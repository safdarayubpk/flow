---
id: 0003
title: Kafka Additional Clarifications
stage: spec
date: 2026-02-10
surface: agent
model: claude-opus-4-5-20251101
feature: 006-kafka-events
branch: 006-kafka-events
user: safdarayub
command: /sp.clarify
labels: ["kafka", "clarification", "spec-refinement", "user-directed"]
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

/sp.clarify
1. For notification consumer (FR-010): start with console logging, but eventually trigger browser notifications / in-app toasts as in Phase V.1 005-advanced-todo-features. Confirm this is ok.

2. Add recurring-instance-created event type to the event types table (missing now).

3. Clarify when reminder-triggered event is published — is it from recurring consumer after scheduling, or from a separate scheduler?

4. Add note that consumers run in single FastAPI process (background tasks via lifespan) — offset not persisted across restarts (limitation for local dev).

5. Suggest adding kcat or Kafka UI in Docker Compose for easy local event inspection/testing.

## Response snapshot

Applied 5 user-directed clarifications to the spec:

1. **FR-010 Updated**: Notification Consumer starts with console logging, future extension to browser notifications/in-app toasts (Phase V.1 pattern)
2. **Event Table**: Added `recurring-instance-created` event type with payload: task_id, parent_task_id, title, scheduled_date
3. **FR-005 Clarified**: reminder-triggered published by existing Phase V.1 scheduler, not Kafka consumers
4. **Assumptions Updated**: Consumer offsets not persisted across restarts (local dev limitation)
5. **Docker Compose**: Added Kafka UI (Redpanda Console/kafka-ui) and optional kcat for debugging

Added FR-024 for recurring-instance-created event publishing.

## Outcome

- ✅ Impact: 5 clarifications applied, 1 new FR added, event table expanded
- 🧪 Tests: N/A (specification phase)
- 📁 Files: spec.md updated
- 🔁 Next prompts: /sp.plan
- 🧠 Reflection: User-directed clarifications filled gaps around event flow and dev tooling

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): All clarifications integrated successfully
- Prompt variant (if applicable): User-directed batch clarification
- Next experiment (smallest change to try): N/A
