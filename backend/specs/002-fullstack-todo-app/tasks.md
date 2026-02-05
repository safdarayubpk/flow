# Tasks: Full-Stack Multi-User Web Application for Todo App

**Feature**: 002-fullstack-todo-app | **Date**: 2026-01-19
**Input**: Implementation plan from `/specs/002-fullstack-todo-app/plan.md`

## Implementation Strategy

Deliver an MVP with User Story 1 (authentication) and US2 (basic task operations) implemented first. Each user story is independently testable and delivers value. User Story 3 (secure data isolation) is implemented throughout all other stories.

## Dependencies

User Story 2 (Manage Personal Tasks) depends on User Story 1 (Create Account and Login) for authentication. User Story 3 (Secure Data Isolation) is a cross-cutting concern implemented throughout both US1 and US2.

## Parallel Execution Examples

- Backend authentication API (US1) can be developed in parallel with frontend authentication UI (US1)
- Task model (US2) can be developed in parallel with user model (US1)
- Frontend task list UI (US2) can be developed in parallel with backend task API endpoints (US2)

---

## Phase 1: Setup

### Goal
Initialize project structure and configure development environment per implementation plan.

### Independent Test
Verify project structure matches plan.md and dependencies can be installed/run.

- [X] T001 Create backend directory structure per implementation plan
- [X] T002 Create frontend directory structure per implementation plan
- [X] T003 [P] Initialize backend requirements.txt with FastAPI, SQLModel, PyJWT, Better Auth dependencies
- [X] T004 [P] Initialize frontend package.json with Next.js 16+, Tailwind CSS, and related dependencies
- [X] T005 Create .env.example files for both backend and frontend
- [X] T006 Set up gitignore for Python and Node.js projects
- [X] T007 Create README.md with project overview and setup instructions

---

## Phase 2: Foundational

### Goal
Establish core infrastructure and foundational components that block all user stories.

### Independent Test
Verify that authentication, database connection, and basic security are functional.

- [X] T008 Set up SQLModel database configuration in backend/src/core/config.py
- [X] T009 Implement JWT authentication utilities in backend/src/core/security.py
- [X] T010 Configure CORS and security middleware in backend/src/main.py
- [X] T011 Create database models base class in backend/src/models/__init__.py
- [X] T012 Set up database connection and session in backend/src/core/database.py
- [X] T013 [P] Create httpOnly cookie utility functions for JWT storage per ADR-001
- [X] T014 [P] Implement user isolation helper functions per ADR-002

---

## Phase 3: User Story 1 - Create Account and Login (Priority: P1)

### Goal
Enable new users to create accounts and existing users to log in securely with JWT token management.

### Independent Test
Register a new account, log in, and verify JWT token is issued and stored securely. Deliver core value of personalized experience.

### Implementation Tasks

#### Models
- [X] T015 Create User model in backend/src/models/user.py per data-model.md specification

#### Services
- [X] T016 Create UserService in backend/src/services/auth.py for user registration/login
- [X] T017 Implement password hashing and verification in auth service

#### API Endpoints
- [X] T018 Create authentication API router in backend/src/api/v1/auth.py
- [X] T019 Implement user registration endpoint POST /api/auth/register
- [X] T020 Implement user login endpoint POST /api/auth/login
- [X] T021 Implement user logout endpoint POST /api/auth/logout

#### Frontend Components
- [X] T022 Create AuthProvider component in frontend/src/components/AuthProvider.tsx
- [X] T023 Create login page in frontend/src/app/login/page.tsx
- [X] T024 Create signup page in frontend/src/app/signup/page.tsx
- [X] T025 Implement useAuth hook in frontend/src/hooks/useAuth.ts
- [X] T026 Create authentication API utilities in frontend/src/lib/auth.ts

#### Security Implementation
- [X] T027 Store JWT tokens in httpOnly cookies per ADR-001
- [X] T028 Implement proper CSRF protection for authentication endpoints

---

## Phase 4: User Story 2 - Manage Personal Tasks (Priority: P1)

### Goal
Allow logged-in users to add, view, update, and delete personal tasks with completion toggling.

### Independent Test
Log in and perform all CRUD operations on tasks. Deliver core value of task management.

### Implementation Tasks

#### Models
- [X] T029 Create Task model in backend/src/models/task.py per data-model.md specification with soft delete per ADR-003

#### Services
- [X] T030 Create TaskService in backend/src/services/task_service.py with user isolation per ADR-002
- [X] T031 Implement create task functionality with user_id assignment
- [X] T032 Implement get user tasks with user_id filtering per ADR-002
- [X] T033 Implement update task functionality with ownership validation
- [X] T034 Implement delete task functionality (soft delete per ADR-003)
- [X] T035 Implement toggle completion functionality with ownership validation

#### API Endpoints
- [X] T036 Create tasks API router in backend/src/api/v1/tasks.py
- [X] T037 Implement GET /api/tasks to list current user's tasks with user_id filter per ADR-002
- [X] T038 Implement POST /api/tasks to create new task with user_id assignment
- [X] T039 Implement GET /api/tasks/{id} to get single task with ownership validation
- [X] T040 Implement PUT /api/tasks/{id} to update task with ownership validation
- [X] T041 Implement DELETE /api/tasks/{id} to delete task (soft delete per ADR-003)
- [X] T042 Implement PATCH /api/tasks/{id}/complete to toggle completion with ownership validation
- [X] T043 Add proper authentication and authorization to all task endpoints

#### Frontend Components
- [X] T044 Create TaskCard component in frontend/src/components/TaskCard.tsx
- [X] T045 Create TaskForm component in frontend/src/components/TaskForm.tsx
- [X] T046 Create TaskList component in frontend/src/components/TaskList.tsx
- [X] T047 Create tasks page in frontend/src/app/tasks/page.tsx
- [X] T048 Create individual task page in frontend/src/app/tasks/[id]/page.tsx
- [X] T049 Implement task API utilities in frontend/src/lib/api.ts

#### Validation
- [X] T050 Implement task title validation (1-200 characters) per spec.md
- [X] T051 Implement proper error handling and validation responses

---

## Phase 5: User Story 3 - Secure Data Isolation (Priority: P1)

### Goal
Ensure tasks are completely isolated between users with no cross-user data access.

### Independent Test
Test with multiple users having overlapping task titles and verify they cannot access each other's data. Deliver core value of data privacy.

### Implementation Tasks

#### Backend Implementation
- [X] T052 Review all database queries to ensure user_id filtering per ADR-002
- [X] T053 Add comprehensive user ownership validation to all task operations per ADR-002
- [X] T054 Implement proper error responses for unauthorized access attempts
- [X] T055 Add database indexes for user_id and completed fields per data-model.md

#### Testing
- [X] T056 Create integration tests with multiple users to verify data isolation
- [X] T057 Test that User A cannot access User B's tasks
- [X] T058 Test that User A cannot modify User B's tasks

#### Security Validation
- [X] T059 Verify all API endpoints enforce user_id == current_user.id filtering
- [X] T060 Test edge cases where user attempts to access non-owned resources

---

## Phase 6: Polish & Cross-Cutting Concerns

### Goal
Complete the application with proper error handling, validation, and deployment configuration.

### Independent Test
Verify complete application functionality with proper error handling and security.

#### Error Handling
- [X] T061 Implement proper error responses per API contract
- [X] T062 Handle expired JWT tokens gracefully per edge cases in spec.md
- [X] T063 Implement proper validation error responses for task title constraints

#### Cleanup and Soft Delete
- [X] T064 Implement scheduled cleanup for soft-deleted tasks per ADR-003
- [X] T065 Add filtering to exclude soft-deleted tasks from queries per ADR-003

#### Frontend Polish
- [X] T066 Style components with Tailwind CSS per spec.md requirements
- [X] T067 Add loading states and error handling to frontend components
- [X] T068 Implement proper navigation and user flow between pages

#### Testing
- [X] T069 Add comprehensive tests for all user stories
- [X] T070 Test authentication flow end-to-end
- [X] T071 Test task management flow end-to-end
- [X] T072 Test data isolation between users end-to-end

#### Deployment
- [X] T073 Update README.md with complete setup and deployment instructions
- [X] T074 Configure Vercel deployment settings for frontend
- [X] T075 Create Docker configuration for backend if needed