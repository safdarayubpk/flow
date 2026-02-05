---
name: sdd-workflow-enforcer
description: follow spec-driven development, enforce SDD workflow, implement from spec, generate code from plan and tasks, use spec kit plus, run full SDD loop
---

# SDD Workflow Enforcer

## Overview

This skill enforces the complete Spec-Driven Development (SDD) process by ensuring all development follows the prescribed workflow from constitution through implementation. It prevents skipping steps and ensures all code generation traces back to specification artifacts.

## Required SDD Workflow Steps

Always follow the full Spec-Driven Development process in this exact order:

1. **Reference global constitution** from `.specify/memory/constitution.md`
2. **Use `/sp.specify`** for WHAT (feature specification)
3. **Run `/sp.clarify`** to ask questions and resolve ambiguities
4. **Create `/sp.plan`** for technical HOW (architecture and implementation plan)
5. **Generate `/sp.tasks`** for atomic breakdown (executable tasks)
6. **Only then run `/sp.implement`** to generate code

## Enforcement Rules

This skill strictly enforces the following rules:

- **No step skipping**: Every SDD step must be completed in order
- **Traceability requirement**: All code must trace back to a specification artifact
- **Task-driven development**: Never generate code without a referenced task from tasks.md
- **Prohibit manual coding**: No direct file edits outside the SDD loop
- **Validation checkpoint**: Verify each step is complete before proceeding

## Common Scenarios

### New Feature Development
```
1. Review constitution from .specify/memory/constitution.md
2. Run /sp.specify to define WHAT the feature should do
3. Run /sp.clarify to resolve any ambiguities in the spec
4. Run /sp.plan to design the technical implementation
5. Run /sp.tasks to break down implementation into atomic tasks
6. Run /sp.implement to generate code based on tasks
```

### Code Modification
```
1. Reference existing specification if available
2. Update /sp.specify if requirements have changed
3. Run /sp.clarify if changes introduce ambiguity
4. Update /sp.plan if architecture needs adjustment
5. Regenerate /sp.tasks if implementation changes
6. Run /sp.implement based on updated tasks
```

### Bug Fixes
```
1. Document bug in specification if not already covered
2. Run /sp.specify to clarify correct behavior
3. Run /sp.clarify if edge cases need resolution
4. Run /sp.plan for fix approach
5. Run /sp.tasks for fix implementation steps
6. Run /sp.implement to generate corrected code
```

## Prohibited Actions

⚠️ **These actions are forbidden when using SDD workflow:**
- Writing code directly without following the SDD steps
- Skipping `/sp.clarify` when requirements are ambiguous
- Generating code without referencing specific tasks from tasks.md
- Bypassing `/sp.plan` for technical decisions
- Making changes without updating relevant specification artifacts
- Manual file edits outside the SDD workflow

## Important Reminder

⚠️ **All code must trace back to a specification artifact** - Every line of code generated must be linked to a specific task derived from the SDD process to maintain traceability and quality.

## Validation Checklist

Before proceeding with any development:
- [ ] Global constitution referenced from .specify/memory/constitution.md
- [ ] /sp.specify completed for WHAT
- [ ] /sp.clarify run to resolve ambiguities
- [ ] /sp.plan completed for technical HOW
- [ ] /sp.tasks generated for atomic breakdown
- [ ] All code generation references specific tasks from tasks.md
- [ ] No manual file edits outside SDD workflow
