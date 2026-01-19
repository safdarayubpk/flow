---
name: monorepo-spec-navigation
description: place file in monorepo, frontend nextjs folder, backend fastapi, reference specs folder, monorepo structure guidance
---

# Monorepo Spec Navigation

## Overview

This skill provides guidance for correctly placing files and navigating the monorepo structure for the hackathon project. It ensures proper organization of frontend, backend, and specification files according to established conventions.

## File Placement Rules

Always follow these monorepo structure conventions when creating or moving files:

- **Frontend code** → `frontend/` (Next.js application)
- **Backend code** → `backend/` (FastAPI application)
- **Specifications** → `specs/[phase]/` (e.g., `specs/002-fullstack/`)
- **Skills** → `.claude/skills/`
- **Shared utilities** → `utils/` or appropriate shared directory

## Directory Reference Table

| Purpose | Directory | Notes |
|---------|-----------|-------|
| Frontend code | `frontend/` | Next.js application files |
| Backend code | `backend/` | FastAPI application files |
| Specifications | `specs/[phase]/` | e.g., `specs/002-fullstack/`, `specs/001-console-todo-app/` |
| Skills | `.claude/skills/` | Custom Claude skills |
| Assets | `assets/` | Static resources and assets |
| Documentation | `docs/` | Project documentation |
| Utilities | `utils/` | Shared utility functions |

## Specification Referencing

When referencing specifications in code or documentation, use the `@specs/...` syntax:

- Example: `@specs/002-fullstack/api-design.md`
- Maintains clear links between implementation and specification
- Helps maintain traceability between code and requirements

## Best Practices

1. **Always verify the correct directory** before creating new files
2. **Follow the established monorepo structure** to maintain consistency
3. **Use proper referencing syntax** when linking to specifications
4. **Keep related functionality grouped** in appropriate directories
5. **Maintain separation between frontend and backend concerns**

## Important Reminder

⚠️ **Follow monorepo conventions from hackathon specification** - Always ensure files are placed in the correct directories according to the established monorepo structure to maintain consistency and proper organization.

## Validation Checklist

Before placing any file:
- [ ] Determine if it's frontend, backend, or specification content
- [ ] Place in correct directory according to the reference table above
- [ ] Use proper referencing syntax (@specs/...) when linking to specs
- [ ] Confirm it follows the monorepo structure convention
- [ ] Verify that related files remain co-located appropriately
