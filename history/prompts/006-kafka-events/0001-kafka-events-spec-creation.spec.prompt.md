---
id: 0001
title: Kafka Events Spec Creation
stage: spec
date: 2026-02-10
surface: agent
model: claude-opus-4-5-20251101
feature: 006-kafka-events
branch: 006-kafka-events
user: safdarayub
command: /sp.specify
labels: ["kafka", "event-driven", "specification", "phase-v2"]
links:
  spec: specs/006-kafka-events/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/006-kafka-events/spec.md
  - specs/006-kafka-events/checklists/requirements.md
tests:
  - null
---

## Prompt

Phase V.2: Kafka – Event-Driven Architecture

Target audience: Beginner who understands basic Kafka concepts (topics, producers, consumers, events) but has no hands-on experience.

Focus: Add simple Kafka-based event publishing and consuming to the existing Todo app from Phase 005-advanced-todo-features, without breaking any existing functionality (REST API, UI, AI chat, user isolation).

Core goals:
- Publish task-related events to Kafka (created, updated, completed, deleted, reminder-triggered, recurring-task-created)
- Create at least 2 simple consumers:
  - Notification consumer: reacts to events like task-created or reminder-triggered → sends reminders/toasts
  - Recurring consumer: reacts to recurring-task-created → schedules future instances
- Keep strict user isolation: every event must include user_id
- Reuse existing Neon DB — no new database
- Use simple local Kafka setup via Docker Compose (1 broker + Zookeeper)
- Maintain 100% backward compatibility: existing CRUD, AI chat, and UI must work unchanged

Success criteria:
- Every task operation publishes a clear JSON event
- Consumers reliably process events (e.g. notification sent, recurring task scheduled)
- No event loss/duplication
- Simple `docker-compose up` to run Kafka locally
- At least 3 event types implemented and demonstrated

Constraints:
- Do NOT break existing REST API, UI, AI chat, or user isolation
- Prefer simple implementation (no cloud Kafka, no complex partitioning yet)
- Use existing skills heavily (fastapi-todo-advanced-endpoints, user-isolation-enforcer, kafka-producer-pattern, kafka-consumer-pattern)
- Add new skills only if absolutely needed

Not building in this sub-phase:
- Dapr integration (save for V.3)
- Cloud deployment (save for V.4)
- Voice/multi-language (bonuses)

## Response snapshot

Created feature specification for Phase V.2: Kafka Event-Driven Architecture with:
- 5 user stories covering event publishing, notification consumer, recurring consumer, local Kafka setup, and backward compatibility
- 21 functional requirements defining event types, consumer behavior, and compatibility constraints
- 10 measurable success criteria
- Edge cases for Kafka unavailability, malformed events, and user isolation
- Event schema and payload documentation
- Checklist validation passed (all items complete)

## Outcome

- ✅ Impact: Feature specification created, branch 006-kafka-events checked out
- 🧪 Tests: N/A (specification phase)
- 📁 Files: spec.md, checklists/requirements.md created
- 🔁 Next prompts: /sp.clarify or /sp.plan
- 🧠 Reflection: Spec covers beginner-friendly Kafka integration with clear boundaries

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Checklist validation PASS (all items complete)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
