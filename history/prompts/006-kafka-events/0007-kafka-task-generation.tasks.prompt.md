---
id: "0007"
title: "Kafka Task Generation"
stage: tasks
date: 2026-02-10
surface: agent
model: claude-opus-4-5
feature: 006-kafka-events
branch: 006-kafka-events
user: safdarayub
command: /sp.tasks
labels: ["tasks", "kafka", "event-driven", "implementation-plan"]
links:
  spec: specs/006-kafka-events/spec.md
  ticket: null
  adr: history/adr/0001-kafka-infrastructure-stack.md, history/adr/0002-event-publishing-strategy.md, history/adr/0003-consumer-execution-model.md
  pr: null
files:
  - specs/006-kafka-events/tasks.md
tests:
  - null
---

## Prompt

Before you generate tasks for 006-kafka-events, do the following silently and internally:
1. Re-read the full current spec.md
2. Re-read the plan.md
3. Re-read the 3 new ADRs and confirm alignment
4. Recall relevant skills (kafka-producer-pattern, kafka-consumer-pattern, etc.)
5. Make mental checklist of constraints
6. Reply with confirmation sentence then generate tasks

Prioritize tasks in this logical order:
1. Docker Compose setup
2. Environment variables and configuration
3. Kafka producer integration
4. Event publishing from task service layer
5. Notification consumer as background task
6. Recurring consumer as background task
7. Integration testing and verification
8. Documentation updates

## Response snapshot

Generated 50 atomic, numbered tasks organized into 8 phases:

- **Phase 1: Setup** (T001-T004) - Docker Compose, dependencies, config
- **Phase 2: Foundational** (T005-T009) - Producer infrastructure
- **Phase 3: US4** (T010-T013) - Local Kafka dev environment
- **Phase 4: US1** (T014-T022) - Task events publishing
- **Phase 5: US5** (T023-T026) - Backward compatibility verification
- **Phase 6: US2** (T027-T034) - Notification consumer
- **Phase 7: US3** (T035-T042) - Recurring task consumer
- **Phase 8: Polish** (T043-T050) - Integration and docs

All tasks follow checklist format with [P], [Story] markers and file paths.

## Outcome

- ✅ Impact: 50 tasks generated covering all 5 user stories and 10 success criteria
- 🧪 Tests: Test tasks included (T045-T050) for unit and integration testing
- 📁 Files: specs/006-kafka-events/tasks.md created
- 🔁 Next prompts: /sp.implement to execute tasks
- 🧠 Reflection: Tasks properly aligned with ADRs; kafka-producer-pattern and kafka-consumer-pattern skills referenced in appropriate tasks

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS - All tasks have checkbox, ID, story label (where applicable), and file paths
- Prompt variant (if applicable): Standard /sp.tasks command with prioritization guidance
- Next experiment (smallest change to try): None needed - task generation successful
