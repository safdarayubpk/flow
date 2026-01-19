---
description: "Task list for Console Todo App implementation"
---

# Tasks: Console Todo App

**Input**: Design documents from `/specs/001-console-todo-app/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: No explicit tests requested in the feature specification, so test tasks are not included.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Console app**: `src/` at repository root
- Paths shown below assume single console project - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project structure per implementation plan in src/
- [x] T002 [P] Create src directory and initialize Python project structure
- [x] T003 [P] Create README.md with project overview and setup instructions

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Create base Task data model in src/task_model.py
- [x] T005 Create TaskManager for in-memory storage in src/task_manager.py
- [x] T006 [P] Create utility functions in src/utils.py
- [x] T007 Create CLI interface base structure in src/cli_interface.py
- [x] T008 Create main application entry point in src/main.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - View Task List (Priority: P1) 🎯 MVP

**Goal**: Enable users to see all tasks displayed in a clear, numbered list so they can quickly understand what they need to do and track which tasks are complete.

**Independent Test**: Launch the app and select "list tasks" from the menu. Should display appropriate message whether zero or multiple tasks exist.

### Implementation for User Story 1

- [x] T009 [P] [US1] Implement Task class with proper string representation in src/task_model.py
- [x] T010 [P] [US1] Implement list_tasks method in src/task_manager.py
- [x] T011 [US1] Implement format_task_list utility function in src/utils.py
- [x] T012 [US1] Implement handle_view_tasks method in src/cli_interface.py
- [x] T013 [US1] Integrate view tasks functionality with main menu in src/main.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Add New Task (Priority: P1)

**Goal**: Enable users to add new tasks with a title and optional description so they can capture what they need to do.

**Independent Test**: Select "add" from the menu, enter task details, and verify the task appears in the list.

### Implementation for User Story 2

- [x] T014 [P] [US2] Enhance Task class with validation in src/task_model.py
- [x] T015 [P] [US2] Implement create_task method in src/task_manager.py
- [x] T016 [US2] Implement get_non_empty_string_input utility in src/utils.py
- [x] T017 [US2] Implement handle_add_task method in src/cli_interface.py
- [x] T018 [US2] Integrate add task functionality with main menu in src/main.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Mark Task Complete/Incomplete (Priority: P2)

**Goal**: Enable users to toggle the completion status of tasks so they can track their progress.

**Independent Test**: Add a task, mark it complete, view the updated status, then mark it incomplete again.

### Implementation for User Story 3

- [x] T019 [P] [US3] Enhance Task class with toggle_completion method in src/task_model.py
- [x] T020 [US3] Implement toggle_task_completion method in src/task_manager.py
- [x] T021 [US3] Implement handle_toggle_completion method in src/cli_interface.py
- [x] T022 [US3] Integrate toggle completion functionality with main menu in src/main.py

**Checkpoint**: At this point, User Stories 1, 2 AND 3 should all work independently

---

## Phase 6: User Story 4 - Update Task Details (Priority: P3)

**Goal**: Enable users to modify the title or description of existing tasks so they can correct mistakes or add more detail.

**Independent Test**: Add a task, update its title and/or description, and verify changes persist in the list view.

### Implementation for User Story 4

- [x] T023 [US4] Implement update_task method in src/task_manager.py
- [x] T024 [US4] Implement handle_update_task method in src/cli_interface.py
- [x] T025 [US4] Integrate update task functionality with main menu in src/main.py

**Checkpoint**: At this point, User Stories 1, 2, 3 AND 4 should all work independently

---

## Phase 7: User Story 5 - Delete Task (Priority: P3)

**Goal**: Enable users to remove tasks they no longer need so their list stays relevant and uncluttered.

**Independent Test**: Add a task, delete it, and verify it no longer appears in the list.

### Implementation for User Story 5

- [x] T026 [US5] Implement delete_task method in src/task_manager.py
- [x] T027 [US5] Implement confirm_action utility function in src/utils.py
- [x] T028 [US5] Implement handle_delete_task method in src/cli_interface.py
- [x] T029 [US5] Integrate delete task functionality with main menu in src/main.py

**Checkpoint**: All user stories should now be independently functional

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T030 [P] Add comprehensive error handling for all operations in src/cli_interface.py
- [x] T031 [P] Add input validation functions in src/utils.py
- [x] T032 [P] Add graceful exit handling with keyboard interrupt support in src/main.py
- [x] T033 [P] Add docstrings and type hints to all modules
- [x] T034 Run quickstart validation to ensure all features work as expected

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 5 (P3)**: Can start after Foundational (Phase 2) - No dependencies on other stories

### Within Each User Story

- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all components for User Story 1 together:
Task: "Implement Task class with proper string representation in src/task_model.py"
Task: "Implement list_tasks method in src/task_manager.py"
Task: "Implement format_task_list utility function in src/utils.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. Complete Phase 4: User Story 2
5. **STOP and VALIDATE**: Test User Stories 1 & 2 independently
6. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo
3. Add User Story 2 → Test independently → Deploy/Demo (MVP!)
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add User Story 5 → Test independently → Deploy/Demo
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
   - Developer D: User Story 4
   - Developer E: User Story 5
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify functionality after each task or logical group
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence