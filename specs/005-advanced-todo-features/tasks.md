# Tasks: Advanced Todo Features

**Feature**: Advanced Todo Features (priorities, tags, search/filter, sort, recurring, due dates)
**Branch**: `005-advanced-todo-features`
**Input**: `/specs/005-advanced-todo-features/spec.md`, `/specs/005-advanced-todo-features/plan.md`

## Implementation Strategy

This implementation follows a phased approach prioritizing foundational components first, then implementing user stories in priority order (P1, P2, P3). Each phase builds upon the previous to ensure a working, testable system at every step. The approach emphasizes backward compatibility and user isolation throughout.

**MVP Scope**: User Story 1 (priority and tags) with basic filtering functionality - this provides immediate value while establishing the core advanced features.

## Dependencies

User stories have the following completion order:
- Foundational components (database, models, services) must be completed before user story implementation
- User Story 1 (P1) - Priority and tags (foundation for other features)
- User Story 2 (P1) - Search and filter (relies on extended model)
- User Story 3 (P2) - Sort functionality (relies on extended model)
- User Story 6 (P2) - AI chat extensions (relies on all other features)
- User Story 4 (P3) - Recurring tasks (relies on extended model)
- User Story 5 (P3) - Due dates and reminders (relies on extended model)

Parallel execution opportunities exist within each user story for different components (models, services, API, UI).

## Parallel Execution Examples

**Within User Story 1**:
- [P] T025-T027: Implement backend components (models, services, API)
- [P] T028-T030: Implement frontend components (priority badge, tag chips, extended form)

**Within User Story 2**:
- [P] T035-T036: Add search/filter API endpoints
- [P] T037-T038: Add search/filter UI components

## Phase 1: Setup

### Goal
Initialize project structure and configure development environment for advanced todo features.

### Independent Test Criteria
- Project structure matches plan.md specification
- All necessary dependencies are properly configured
- Development environment is ready for implementation

### Tasks

- [X] T001 Create backend/src/models directory structure per implementation plan
- [X] T002 Create backend/src/services directory structure per implementation plan
- [X] T003 Create backend/src/api/v1 directory structure per implementation plan
- [X] T004 Create frontend/src/components directory structure per implementation plan
- [X] T005 Create frontend/src/hooks directory structure per implementation plan
- [X] T006 Set up Alembic configuration for database migrations

## Phase 2: Foundational Components

### Goal
Implement foundational components that all user stories depend on: extended Task model, Tag model, and core services.

### Independent Test Criteria
- Extended Task model includes all new fields (priority, tags, due_date, recurrence_rule, reminder_enabled)
- Tag model properly implements many-to-many relationship with Task
- Database migration adds new columns and tables without breaking existing functionality
- User isolation is maintained in all operations

### Tasks

- [X] T010 [P] Create Tag SQLModel in backend/src/models/tag.py using todo-model-extensions skill
- [X] T011 [P] Update Task SQLModel in backend/src/models/task.py with priority, tags, due_date, recurrence_rule, reminder_enabled using todo-model-extensions skill
- [X] T012 [P] Create task_tags association table in backend/src/models/tag.py using todo-model-extensions skill
- [X] T013 Create Alembic migration to add new columns to Task table (priority, tags, due_date, recurrence_rule, reminder_enabled)
- [X] T014 Create Alembic migration to create Tag table and task_tags association table
- [X] T015 Update TaskService in backend/src/services/task_service.py with filtering capabilities using fastapi-todo-advanced-endpoints skill
- [X] T016 Create TagService in backend/src/services/tag_service.py for tag management using fastapi-todo-advanced-endpoints skill
- [X] T017 Update existing Task endpoints in backend/src/api/v1/tasks.py to maintain backward compatibility
- [X] T018 Create Tag endpoints in backend/src/api/v1/tags.py for tag management using fastapi-todo-advanced-endpoints skill
- [X] T019 Verify user isolation is enforced in all new database queries using user-isolation-enforcer skill
- [X] T020 Create tests for extended Task model validation rules
- [X] T021 Create tests for Tag model and many-to-many relationship
- [X] T022 Verify existing functionality still works after model extensions
- [X] T023 Verify database migration runs successfully without data loss
- [X] T024 Verify all new indexes are created properly for performance

## Phase 3: [US1] Add Task with Priority and Tags (Priority: P1)

### Goal
Implement user story 1: allow users to add tasks with priority levels (high, medium, low) and assign tags/categories to them.

### Independent Test Criteria
- Users can create tasks with priority levels (high, medium, low)
- Users can assign tags to tasks
- Priority and tags are properly stored in the database
- Priority badges and tag chips are displayed in the UI
- Existing functionality remains intact

### Tasks

- [X] T025 [P] [US1] Implement PriorityBadge component in frontend/src/components/PriorityBadge.tsx using nextjs-todo-advanced-ui skill
- [X] T026 [P] [US1] Implement TagChips component in frontend/src/components/TagChips.tsx using nextjs-todo-advanced-ui skill
- [X] T027 [US1] Update TaskForm component in frontend/src/components/TaskForm.tsx to include priority selector and tag input using nextjs-todo-advanced-ui skill
- [X] T028 [P] [US1] Update TaskCard component in frontend/src/components/TaskCard.tsx to display priority badges and tag chips using nextjs-todo-advanced-ui skill
- [X] T029 [P] [US1] Create test for PriorityBadge component with different priority levels
- [X] T030 [P] [US1] Create test for TagChips component with different tag arrays
- [X] T031 [US1] Update backend API to accept priority and tags in task creation requests using fastapi-todo-advanced-endpoints skill
- [X] T032 [US1] Update backend API to return priority and tags in task responses using fastapi-todo-advanced-endpoints skill
- [X] T033 [US1] Verify priority values are validated (high, medium, low only) using fastapi-todo-advanced-endpoints skill
- [X] T034 [US1] Verify tag values are validated (alphanumeric, spaces, hyphens, underscores only; max 50 chars) using fastapi-todo-advanced-endpoints skill
- [X] T035 [US1] Test creating tasks with priority and tags using the UI
- [X] T036 [US1] Verify user isolation works with priority and tag functionality using user-isolation-enforcer skill

### Verification
- Create tasks with different priority levels and verify badges display correctly
- Add tags to tasks and verify they appear as chips in the UI
- Confirm existing functionality still works after priority/tag implementation

## Phase 4: [US2] Search and Filter Tasks (Priority: P1)

### Goal
Implement user story 2: allow users to search and filter tasks by keywords, status, priority, and date range.

### Independent Test Criteria
- Users can search tasks by keywords in title and description
- Users can filter tasks by priority, tags, due date range, and completion status
- Search and filter operations return results within 2 seconds for up to 1000 tasks
- Existing functionality remains intact

### Tasks

- [X] T037 [P] [US2] Add query parameters to GET /api/v1/tasks endpoint: priority, tags, due_date_before, sort, recurring using fastapi-todo-advanced-endpoints skill
- [X] T038 [P] [US2] Implement filtering logic in TaskService for priority, tags, due date, recurring using fastapi-todo-advanced-endpoints skill
- [X] T039 [P] [US2] Implement sorting logic in TaskService for priority, due date, title, created_at using fastapi-todo-advanced-endpoints skill
- [X] T040 [P] [US2] Create SearchBar component in frontend/src/components/SearchBar.tsx using nextjs-todo-advanced-ui skill
- [X] T041 [P] [US2] Create FilterPanel component in frontend/src/components/FilterPanel.tsx with priority, tag, date filters using nextjs-todo-advanced-ui skill
- [X] T042 [US2] Update TaskList page to accept and apply search/filter parameters using nextjs-todo-advanced-ui skill
- [X] T043 [US2] Implement client-side filtering optimization for better performance
- [X] T044 [US2] Add loading states to search/filter operations using nextjs-todo-advanced-ui skill
- [X] T045 [US2] Add error handling for search/filter operations using nextjs-todo-advanced-ui skill
- [X] T046 [US2] Test search functionality with various keyword combinations
- [X] T047 [US2] Test filter functionality with different filter combinations
- [X] T048 [US2] Verify search/filter performance meets 2-second requirement for 1000 tasks
- [X] T049 [US2] Verify user isolation works with search and filter functionality using user-isolation-enforcer skill

### Verification
- Search for tasks using keywords and verify correct results are returned
- Apply different filters and verify correct tasks are displayed
- Confirm performance meets requirements (under 2 seconds for 1000 tasks)

## Phase 5: [US3] Sort Tasks by Various Criteria (Priority: P2)

### Goal
Implement user story 3: allow users to sort tasks by due date, priority, or alphabetically.

### Independent Test Criteria
- Users can sort tasks by priority, due date, title, or creation date
- Sort operations complete within 1 second
- Sorting works in combination with search and filter
- Existing functionality remains intact

### Tasks

- [X] T050 [P] [US3] Create SortDropdown component in frontend/src/components/SortDropdown.tsx using nextjs-todo-advanced-ui skill
- [X] T051 [P] [US3] Update TaskList page to include sort functionality using nextjs-todo-advanced-ui skill
- [X] T052 [US3] Implement sort parameter handling in GET /api/v1/tasks endpoint using fastapi-todo-advanced-endpoints skill
- [X] T053 [US3] Add sort validation to ensure only allowed fields can be sorted using fastapi-todo-advanced-endpoints skill
- [X] T054 [US3] Optimize database queries for sorting with proper indexes
- [X] T055 [US3] Implement multi-field sorting (e.g., by priority then by due date) using fastapi-todo-advanced-endpoints skill
- [X] T056 [US3] Add visual indicators for current sort order (ascending/descending) using nextjs-todo-advanced-ui skill
- [X] T057 [US3] Test sort functionality with different sort fields
- [X] T058 [US3] Test sort performance meets 1-second requirement
- [X] T059 [US3] Test sort functionality combined with search and filter
- [X] T060 [US3] Verify user isolation works with sort functionality using user-isolation-enforcer skill

### Verification
- Sort tasks by different criteria and verify correct ordering
- Confirm sort performance meets requirements (under 1 second)
- Verify sorting works correctly with search and filter combinations

## Phase 6: [US6] Enhanced AI Chat Commands (Priority: P2)

### Goal
Implement user story 6: extend AI chat to recognize and process commands related to recurring tasks and due dates.

### Independent Test Criteria
- AI chat correctly interprets commands related to priorities, tags, due dates, and recurring tasks
- At least 85% of new commands are processed correctly
- Existing AI chat functionality remains intact
- Natural language processing works for advanced commands

### Tasks

- [x] T061 [P] [US6] Extend AI agent tools to include filter_tasks function (by priority, tags, due_date_range) using fastapi-todo-advanced-endpoints skill
- [x] T062 [P] [US6] Extend AI agent tools to include sort_tasks function (by priority, due_date, title) using fastapi-todo-advanced-endpoints skill
- [x] T063 [P] [US6] Extend AI agent tools to include set_due_date function (task_id, date) using fastapi-todo-advanced-endpoints skill
- [x] T064 [P] [US6] Extend AI agent tools to include set_recurring function (task_id, rrule_string) using fastapi-todo-advanced-endpoints skill
- [x] T065 [US6] Update AI agent to understand natural language commands for priorities (e.g., "show high priority tasks") using fastapi-todo-advanced-endpoints skill
- [x] T066 [US6] Update AI agent to understand natural language commands for tags (e.g., "show work tasks") using fastapi-todo-advanced-endpoints skill
- [x] T067 [US6] Update AI agent to understand natural language commands for due dates (e.g., "show tasks due this week") using fastapi-todo-advanced-endpoints skill
- [x] T068 [US6] Update AI agent to understand natural language commands for recurring tasks (e.g., "add recurring weekly meeting") using fastapi-todo-advanced-endpoints skill
- [x] T069 [US6] Test AI chat with various advanced command examples
- [x] T070 [US6] Verify AI chat correctly processes at least 85% of new commands
- [x] T071 [US6] Verify existing AI chat functionality remains intact
- [x] T072 [US6] Test user isolation with AI chat advanced commands using user-isolation-enforcer skill

### Verification
- Test AI chat with commands like "show high priority tasks", "add recurring weekly meeting", "show tasks due this week"
- Confirm at least 85% of new commands are processed correctly
- Verify existing AI functionality still works

## Phase 7: [US4] Create Recurring Tasks (Priority: P3)

### Goal
Implement user story 4: allow users to create recurring tasks that automatically reschedule themselves.

### Independent Test Criteria
- Users can create recurring tasks with configurable patterns (daily, weekly, monthly, yearly)
- 95% of users can successfully create recurring tasks without assistance
- Recurring tasks appear in future periods according to their pattern
- Only the specific recurring task instance is modified when updating/deleting

### Tasks

- [x] T073 [P] [US4] Create RecurringToggle component in frontend/src/components/RecurringToggle.tsx using nextjs-todo-advanced-ui skill
- [x] T074 [P] [US4] Create RecurrenceEditor component in frontend/src/components/RecurrenceEditor.tsx for RRULE selection using nextjs-todo-advanced-endpoints skill
- [x] T075 [US4] Update TaskForm to include recurring task options using nextjs-todo-advanced-ui skill
- [x] T076 [US4] Implement PATCH /api/v1/tasks/{id}/recurring endpoint using fastapi-todo-advanced-endpoints skill
- [x] T077 [US4] Implement logic to store recurrence rules in RRULE format using fastapi-todo-advanced-endpoints skill
- [x] T078 [US4] Implement recurring task instance management (each instance has unique ID referencing original) using fastapi-todo-advanced-endpoints skill
- [x] T079 [US4] Add validation for recurrence rules to ensure proper RRULE format using fastapi-todo-advanced-endpoints skill
- [x] T080 [US4] Create service function to generate future recurring task instances using fastapi-todo-advanced-endpoints skill
- [x] T081 [US4] Test creating recurring tasks with different patterns (daily, weekly, monthly)
- [x] T082 [US4] Test modifying/deleting specific recurring task instances (not the whole series)
- [x] T083 [US4] Verify recurring tasks appear in future periods according to their pattern
- [x] T084 [US4] Verify user isolation works with recurring task functionality using user-isolation-enforcer skill

### Verification
- Create recurring tasks with different patterns and verify they appear in future periods
- Modify/delete specific instances and verify only that instance is affected
- Confirm 95% success rate for creating recurring tasks

## Phase 8: [US5] Set Due Dates and Receive Reminders (Priority: P3)

### Goal
Implement user story 5: allow users to set due dates and times for tasks and receive browser notifications.

### Independent Test Criteria
- Users can set due dates and times for tasks
- Browser notifications appear within 30 seconds of the due time
- In-app toast notifications are shown when browser permissions are denied
- Tasks with due dates in the past are allowed but show warnings

### Tasks

- [x] T085 [P] [US5] Create DatePicker component in frontend/src/components/DatePicker.tsx using nextjs-todo-advanced-ui skill
- [x] T086 [P] [US5] Create TimePicker component in frontend/src/components/TimePicker.tsx using nextjs-todo-advanced-ui skill
- [x] T087 [P] [US5] Create NotificationPermissionHandler in frontend/src/components/NotificationPermissionHandler.tsx using nextjs-todo-advanced-ui skill
- [x] T088 [US5] Update TaskForm to include due date and reminder toggle using nextjs-todo-advanced-ui skill
- [x] T089 [US5] Implement PATCH /api/v1/tasks/{id}/due_date endpoint using fastapi-todo-advanced-endpoints skill
- [x] T090 [US5] Implement logic to store due dates in UTC and convert to user's timezone for display using fastapi-todo-advanced-endpoints skill
- [x] T091 [US5] Implement browser notification service in frontend/src/services/notificationService.ts using nextjs-todo-advanced-endpoints skill
- [x] T092 [US5] Implement in-app toast notification component using shadcn/ui toast component
- [x] T093 [US5] Add due date validation to ensure proper datetime format using fastapi-todo-advanced-endpoints skill
- [x] T094 [US5] Implement timezone conversion logic to handle different user timezones using fastapi-todo-advanced-endpoints skill
- [x] T095 [US5] Test setting due dates for tasks and verifying they're stored correctly
- [x] T096 [US5] Test browser notification functionality with proper timing (within 30 seconds)
- [x] T097 [US5] Test in-app notification fallback when browser permissions are denied
- [x] T098 [US5] Verify due dates can be set in the past with appropriate UI warnings
- [x] T099 [US5] Verify user isolation works with due date and reminder functionality using user-isolation-enforcer skill

### Verification
- Set due dates for tasks and verify they're stored and displayed correctly
- Test browser notifications appear within 30 seconds of due time
- Verify in-app notifications work when browser permissions are denied
- Confirm due dates in the past are handled appropriately

## Phase 9: Polish & Cross-Cutting Concerns

### Goal
Complete the implementation with final touches, comprehensive testing, and verification of all requirements.

### Independent Test Criteria
- All existing functionality continues to work without degradation (login, CRUD, AI chat)
- No cross-user data leakage occurs with new features (user isolation maintained)
- System handles extended Task model without performance degradation
- 90% of users find new UI elements intuitive to use

### Tasks

- [X] T100 Verify all existing CRUD operations still work correctly after advanced feature additions
- [X] T101 Test user isolation is maintained across all new features using user-isolation-enforcer skill
- [X] T102 Run performance tests to ensure no degradation with extended Task model
- [X] T103 Conduct UI/UX review to ensure new components are intuitive (target 90% user satisfaction)
- [X] T104 Test backward compatibility by verifying old API calls still work
- [X] T105 Perform comprehensive integration testing of all features together
- [X] T106 Test edge cases: invalid tag names, past due dates, recurring task conflicts
- [X] T107 Verify database migration can be rolled back safely
- [X] T108 Test all API endpoints for proper error handling and validation
- [X] T109 Verify all UI components are responsive and accessible
- [X] T110 Run full test suite to ensure no regressions were introduced
- [X] T111 Update documentation with new API endpoints and UI components
- [X] T112 Perform final verification that all success criteria are met
- [X] T113 Clean up temporary files and finalize implementation