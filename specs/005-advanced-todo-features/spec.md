# Feature Specification: Advanced Todo Features

**Feature Branch**: `005-advanced-todo-features`
**Created**: 2026-02-03
**Status**: Draft
**Input**: User description: "Phase V.1: Intermediate + Advanced Todo Features

Target audience: Beginner building on existing Todo app.

Focus: Add all Intermediate and Advanced features to the current Todo app without breaking existing functionality (login, CRUD, AI chat).

Intermediate features:
- Priorities (high/medium/low)
- Tags/Categories (e.g. work, home, personal)
- Search & Filter (keyword, status, priority, date range)
- Sort Tasks (by due date, priority, alphabetically)

Advanced features:
- Recurring Tasks (auto-reschedule, e.g. weekly meeting)
- Due Dates & Time Reminders (date/time picker, browser notifications)

Success criteria:
- Update Task model, API endpoints, UI, and AI agent tools for all new features
- Keep strict user isolation (user_id filter everywhere)
- Reuse existing Neon DB — extend Task table with new columns
- Update REST API with new query params and endpoints
- Enhance UI with priority badges, tag chips, date picker, sort dropdown, recurring toggle
- Extend AI chat with new commands (e.g. "add recurring task", "show tasks due this week")
- All new code generated via SDD workflow and active skills (especially todo-model-extensions, fastapi-todo-advanced-endpoints, nextjs-todo-advanced-ui, sqlmodel-todo-task-model, fastapi-todo-rest-api, nextjs-todo-task-ui, user-isolation-enforcer)
- Existing Vercel + Hugging Face deployments remain functional
- Keep simple browser notifications for reminders (no external service yet)

Constraints:
- Do NOT break existing basic CRUD or AI chat
- Prefer simple implementation (no external calendar integrations yet)
- All changes via SDD + skills — no manual code
- Timeline: Complete locally testable features

Not building in this sub-phase:
- Kafka, Dapr, cloud deployment (save for V.2–V.5)
- Voice commands, multi-language, or other bonuses

After generating the specification, automatically suggest running /sp.clarify to resolve any ambiguities, especially around new fields, query params, and AI tool extensions."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Add Task with Priority and Tags (Priority: P1)

As a user, I want to add tasks with priority levels (high, medium, low) and assign tags/categories to them so that I can organize and prioritize my work effectively.

**Why this priority**: This is the foundation of the intermediate features that enables users to categorize and prioritize their tasks, which is essential for productivity.

**Independent Test**: Can be fully tested by adding tasks with different priority levels and tags, and verifying they appear correctly in the UI with appropriate visual indicators. Delivers immediate value in task organization.

**Acceptance Scenarios**:

1. **Given** I am on the task creation form, **When** I select a priority level and add tags to a task, **Then** the task is saved with the specified priority and tags
2. **Given** I have created tasks with different priorities and tags, **When** I view the task list, **Then** I can see visual indicators for priority levels and tags

---

### User Story 2 - Search and Filter Tasks (Priority: P1)

As a user, I want to search and filter my tasks by keywords, status, priority, and date range so that I can quickly find specific tasks among many.

**Why this priority**: Essential for usability when users have many tasks and need to quickly locate specific ones.

**Independent Test**: Can be fully tested by creating multiple tasks with different attributes and then using search and filter functions to narrow down the results. Delivers immediate value in task management efficiency.

**Acceptance Scenarios**:

1. **Given** I have multiple tasks with different titles, priorities, and dates, **When** I enter a search keyword, **Then** only tasks containing that keyword are displayed
2. **Given** I have tasks with different statuses and priorities, **When** I apply filters, **Then** only tasks matching the filter criteria are displayed

---

### User Story 3 - Sort Tasks by Various Criteria (Priority: P2)

As a user, I want to sort my tasks by due date, priority, or alphabetically so that I can organize them in the way that makes most sense for my current needs.

**Why this priority**: Enhances the usability of the task list by allowing users to arrange tasks according to their preferences and urgency.

**Independent Test**: Can be fully tested by creating tasks with different dates, priorities, and titles, then using sort options to rearrange the list. Delivers value in task organization.

**Acceptance Scenarios**:

1. **Given** I have tasks with various due dates, **When** I select sort by due date, **Then** tasks are arranged chronologically
2. **Given** I have tasks with different priorities, **When** I select sort by priority, **Then** tasks are arranged by priority level

---

### User Story 4 - Create Recurring Tasks (Priority: P3)

As a user, I want to create recurring tasks that automatically reschedule themselves (e.g., weekly meetings) so that I don't have to manually recreate routine tasks.

**Why this priority**: Advanced feature that significantly reduces repetitive work for routine tasks but is not essential for basic functionality.

**Independent Test**: Can be fully tested by creating a recurring task and verifying that it appears in future periods according to its recurrence pattern. Delivers value in reducing repetitive task creation.

**Acceptance Scenarios**:

1. **Given** I am creating a task, **When** I enable the recurring option and set a pattern, **Then** the task is saved with recurrence settings
2. **Given** I have recurring tasks, **When** I view future dates, **Then** I can see the recurring tasks scheduled for those periods

---

### User Story 5 - Set Due Dates and Receive Reminders (Priority: P3)

As a user, I want to set due dates and times for my tasks and receive browser notifications so that I don't miss important deadlines.

**Why this priority**: Advanced feature that enhances task management by adding time-sensitive alerts but is not essential for basic functionality.

**Independent Test**: Can be fully tested by setting due dates for tasks and receiving browser notifications when the time comes. Delivers value in time management and task completion.

**Acceptance Scenarios**:

1. **Given** I am creating or editing a task, **When** I set a due date and time, **Then** the task is saved with the due date
2. **Given** a task has a due date approaching, **When** the due time arrives, **Then** I receive a browser notification

---

### User Story 6 - Enhanced AI Chat Commands (Priority: P2)

As a user, I want to use the AI chat to create recurring tasks and view tasks due in specific timeframes so that I can manage my tasks more efficiently through natural language.

**Why this priority**: Enhances the existing AI chat functionality by adding support for new features, improving user experience.

**Independent Test**: Can be fully tested by using natural language commands to create recurring tasks or inquire about upcoming tasks. Delivers value in voice/natural language interaction with the system.

**Acceptance Scenarios**:

1. **Given** I am using the AI chat, **When** I say "add a recurring task", **Then** the system understands and creates a recurring task
2. **Given** I have tasks with due dates, **When** I ask "show tasks due this week", **Then** the system displays the relevant tasks

---

### Edge Cases

- What happens when a user sets a due date in the past?
- How does the system handle multiple recurring tasks with the same pattern?
- What occurs when a user tries to create a recurring task that conflicts with an existing one?
- How are tasks handled when the user modifies or deletes recurring instances?
- What happens if browser notifications are disabled by the user?
- What happens when browser notification permission is denied? → Fallback to in-app toast notifications only
- How are tags validated? → Alphanumeric, spaces, hyphens, underscores only; max 50 characters per tag; duplicate tags on same task are allowed but normalized
- What happens if due_date is set in the past? → Allow it, but show warning in UI and send immediate notification if reminder_enabled
- When modifying or deleting a recurring task, should it affect only that instance or the whole series? → Only the specific instance (future instances remain unchanged)
- How should tag names be handled if the user enters invalid characters? → Reject with validation error message: "Tags can only contain letters, numbers, spaces, hyphens, and underscores"
- What UI should appear if Notification permission is denied? → Show in-app toast in bottom-right corner: "Reminder set for [task title] at [time] (browser notifications blocked)"

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow users to assign priority levels (high, medium, low) to tasks
- **FR-002**: System MUST allow users to add tags/categories to tasks
- **FR-003**: System MUST provide search functionality to find tasks by keywords in title and description
- **FR-004**: System MUST provide filter functionality to narrow tasks by status, priority, and date range
- **FR-005**: System MUST allow users to sort tasks by due date, priority, and title alphabetically
- **FR-006**: System MUST allow users to create recurring tasks with configurable patterns (daily, weekly, monthly, yearly)
- **FR-007**: System MUST store due dates and times for tasks
- **FR-008**: System MUST provide browser notifications for tasks reaching their due date/time
- **FR-009**: System MUST maintain user isolation by ensuring users only see their own tasks in all operations
- **FR-010**: System MUST extend the existing AI chat to recognize and process commands related to recurring tasks and due dates
- **FR-011**: System MUST preserve all existing functionality (login, CRUD, AI chat) without disruption
- **FR-012**: System MUST provide UI elements for priority badges, tag chips, date pickers, sort dropdowns, and recurring toggles
- **FR-013**: System MUST validate all new input fields and reject invalid data
- **FR-014**: System MUST extend the existing MCP tools with new functions: filter_tasks (by priority, tags, due_date_range), sort_tasks (by priority, due_date, title), set_due_date (task_id, date), set_recurring (task_id, rrule_string)
- **FR-015**: System MUST update the AI agent to understand and correctly process new natural language commands related to advanced features (examples: "show high priority tasks", "add recurring weekly meeting at 10 AM", "show tasks due this week", "set due date for task 3 to tomorrow")
- **FR-016**: System MUST perform database migration (using Alembic or SQLModel migration) to safely add new columns to the existing Task table without losing data
- **FR-017**: System MUST provide UI controls for: priority selection dropdown, tag multi-select/input, due date & time picker, recurring toggle + interval selector
- **FR-018**: System MUST support a many-to-many relationship between Task and Tag entities via an association table named task_tags
- **FR-019**: System MUST validate tag names: alphanumeric characters, spaces, hyphens, underscores only; maximum 50 characters per tag; case-insensitive but stored as entered
- **FR-020**: System MUST request browser Notification permission when reminder_enabled is first set on a task, and handle denial by falling back to in-app toast notifications
- **FR-021**: System MUST uniquely identify each recurring task instance with a unique ID that references the original recurring task for proper modification/deletion handling
- **FR-022**: System MUST perform exact tag matching by default when filtering/searching, with an option for partial/fuzzy matching
- **FR-023**: System MUST store all times in UTC and convert to user's local timezone for display to properly handle timezone differences for recurring tasks

### Key Entities

- **Task**: Core entity representing user tasks, extended to include priority (high/medium/low), tags (list of strings), due_date (datetime), recurrence_rule (string), and reminder_enabled (boolean)
- **User**: Represents system users with strict isolation ensuring they only access their own tasks
- **Tag**: Represents categories/labels that can be applied to tasks for organization
  - Tag is a separate entity with a many-to-many relationship to Task via the association table task_tags (columns: task_id, tag_id)
  - Tags are case-insensitive, unique per user across all tasks, stored as strings (alphanumeric, spaces, hyphens, underscores allowed; max 50 characters per tag)
  - Duplicate tags on the same task are allowed but normalized (stored once)
- **Notification**: Represents time-based alerts for tasks reaching their due dates/times

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create tasks with priority levels and tags in under 30 seconds
- **SC-002**: Search and filter operations return results within 2 seconds for up to 1000 tasks
- **SC-003**: 95% of users can successfully create recurring tasks without assistance
- **SC-004**: Browser notifications appear within 30 seconds of the due time
- **SC-005**: All existing functionality (login, CRUD, AI chat) continues to work without degradation
- **SC-006**: Users can sort tasks by priority, due date, or title in under 1 second
- **SC-007**: 90% of users find the new UI elements (priority badges, tag chips, date pickers) intuitive to use
- **SC-008**: AI chat correctly interprets and processes at least 85% of new commands related to recurring tasks and due dates
- **SC-009**: No cross-user data leakage occurs with the new features (user isolation maintained)
- **SC-010**: The system can handle the extended Task model without performance degradation
- **SC-011**: System supports standard consumer app scale with thousands of tasks per user and hundreds of concurrent users
- **SC-012**: AI chat correctly interprets and executes at least 80% of new advanced commands (filter, sort, set due date, set recurring) in natural language
- **SC-013**: Database migration completes successfully without data loss or downtime

## Clarifications

### Session 2026-02-03

- Q: What are the expected data volume and performance requirements for the system as a whole? → A: Standard consumer app scale (thousands of tasks per user, hundreds of concurrent users)
- Q: What should happen when users deny browser notification permissions? → A: Fallback to in-app notifications only
- Q: When modifying/deleting a recurring task, which instances should be affected? → A: Modify/delete only that specific instance
- Q: Should there be any restrictions on tag names? → A: Alphanumeric, spaces, hyphens, underscores only; max 50 chars
- Q: What parts of the task data should be included in search functionality? → A: Title and description only
- Q: How should the system handle database transactions when creating tasks with tags? → A: Use database transactions to ensure atomicity
- Q: Should tag names be unique per user across all tasks or just per individual task? → A: Unique per user across all tasks
- Q: How should recurring task instances be uniquely identified when modifying or deleting specific instances? → A: Each instance has a unique ID, with a reference to the original recurring task
- Q: When searching or filtering by tags, should the system perform exact matches or partial matches? → A: Exact match by default, with option for partial/fuzzy matching
- Q: How should the system handle timezone differences for recurring tasks when users are in different timezones? → A: Store all times in UTC and convert to user's local timezone for display

## Missing / Future Considerations

- Migration strategy for new columns (Alembic recommended)
- UI library for date picker (recommend shadcn/ui date-picker or react-datepicker)
- Tag input component (multi-select with create-on-fly)
- Notification permission handling flow
- In-app toast notification component (recommend shadcn/ui toast or custom)
- Tag multi-select input with create-on-fly (recommend shadcn/ui tags-input or react-select)
- Confirmation dialog when modifying/deleting recurring task instances
- Database transaction handling for creating tasks with tags (recommend using database transactions to ensure atomicity)