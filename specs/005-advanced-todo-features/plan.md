# Implementation Plan: Advanced Todo Features

**Branch**: `005-advanced-todo-features` | **Date**: 2026-02-03 | **Spec**: [link to spec.md](spec.md)
**Input**: Feature specification from `/specs/005-advanced-todo-features/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This plan extends the existing todo application with intermediate and advanced features including priorities (high/medium/low), tags/categories, search & filter capabilities, sort functionality, recurring tasks, and due dates with time reminders. The implementation extends the existing Task model with new fields while maintaining strict user isolation and backward compatibility with existing functionality (login, CRUD, AI chat). The approach involves extending the SQLModel Task entity, updating API endpoints with advanced query parameters, enhancing the UI with new components (priority badges, tag chips, date pickers), and extending AI chat capabilities.

## Technical Context

**Language/Version**: Python 3.13, TypeScript 5.0, Next.js 16+
**Primary Dependencies**: FastAPI, SQLModel, Neon PostgreSQL, Better Auth, shadcn/ui, Tailwind CSS
**Storage**: Neon PostgreSQL database with existing schema extended via Alembic migrations
**Testing**: pytest for backend, Jest/React Testing Library for frontend
**Target Platform**: Web application (Next.js frontend + FastAPI backend) with Kubernetes deployment
**Project Type**: Web application (frontend + backend)
**Performance Goals**: Search/filter operations return results within 2 seconds for up to 1000 tasks, 95% of users can successfully create recurring tasks without assistance, AI chat correctly interprets 85% of new commands
**Constraints**: Must NOT break existing basic CRUD or AI chat functionality, reuse existing Neon DB, maintain strict user isolation (user_id filter everywhere), all changes via SDD workflow and active skills
**Scale/Scope**: Standard consumer app scale (thousands of tasks per user, hundreds of concurrent users)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **SDD Compliance**: ✓ All implementation follows SDD methodology with specs, plans, and tasks completed before code generation
- **AI-Only Implementation**: ✓ All code will be generated exclusively by Claude Code, no manual code writing
- **Security and Isolation**: ✓ User authentication with JWT tokens via Better Auth, all data queries include per-user filtering
- **Tech Stack Compliance**: ✓ Using approved technology stack (FastAPI, Next.js, SQLModel, Neon PostgreSQL, Better Auth)
- **Cloud-Native Readiness**: ✓ Services designed for loose coupling, configuration externalized for Kubernetes deployment
- **Reusability and Modularity**: ✓ Using active skills (todo-model-extensions, fastapi-todo-advanced-endpoints, nextjs-todo-advanced-ui) for modular implementation

## Project Structure

### Documentation (this feature)

```text
specs/005-advanced-todo-features/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command output)
├── data-model.md        # Phase 1 output (/sp.plan command output)
├── quickstart.md        # Phase 1 output (/sp.plan command output)
├── contracts/           # Phase 1 output (/sp.plan command output)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── task.py          # Extended Task model with priority, tags, due_date, recurrence, reminder
│   │   └── user.py          # User model with relationships
│   ├── services/
│   │   ├── task_service.py  # Task service with extended filtering/sorting capabilities
│   │   └── tag_service.py   # Tag service for tag management
│   ├── api/
│   │   └── v1/
│   │       ├── tasks.py     # Extended task endpoints with query parameters
│   │       └── auth.py      # Authentication endpoints
│   ├── core/
│   │   ├── database.py      # Database configuration
│   │   ├── auth.py          # Authentication utilities
│   │   └── config.py        # Configuration settings
│   └── main.py              # FastAPI application entry point
└── tests/
    ├── unit/
    ├── integration/
    └── contract/

frontend/
├── src/
│   ├── app/
│   │   ├── tasks/
│   │   │   ├── page.tsx     # Task list page with advanced filtering/sorting
│   │   │   └── [id]/
│   │   │       └── page.tsx # Task detail page
│   │   └── globals.css      # Global styles
│   ├── components/
│   │   ├── TaskForm.tsx     # Extended task form with priority, tags, due date, recurrence
│   │   ├── TaskCard.tsx     # Task display with priority badges and tag chips
│   │   ├── PriorityBadge.tsx # Priority badge component
│   │   ├── TagChips.tsx     # Tag chips component
│   │   ├── DatePicker.tsx   # Date picker component
│   │   └── SortDropdown.tsx # Sort dropdown component
│   ├── lib/
│   │   ├── api.ts           # API utilities
│   │   └── auth.ts          # Authentication utilities
│   └── hooks/
│       └── useTaskFilters.ts # Hook for task filtering and sorting
└── tests/
    ├── unit/
    └── integration/
```

**Structure Decision**: Web application structure with separate backend (FastAPI) and frontend (Next.js) to maintain separation of concerns and enable independent scaling. The backend provides REST API endpoints for the frontend to consume, with extended functionality for the new features.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | | |