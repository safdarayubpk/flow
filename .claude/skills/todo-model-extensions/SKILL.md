---
name: todo-model-extensions
description: Extend todo task sqlmodel, add priority tags due_date recurring reminder fields to Task model. Always preserves existing fields (id, user_id, title, description, completed, created_at, updated_at) and maintains backward compatibility. Use when modifying Task model with new fields like priority, tags, due_date, recurrence, and reminders.
---

# Todo Model Extensions

## Overview

This skill provides guidance for extending the existing Task SQLModel with additional fields while maintaining backward compatibility and preserving existing functionality. It helps developers add priority, tags, due_date, recurrence, and reminder fields to the Task model following SQLModel best practices.

## Extension Guidelines

When extending the Task model, always preserve existing fields and follow these patterns:

### Required Existing Fields (Preserve These)
- `id`: Primary key (auto-generated)
- `user_id`: Foreign key with index for user isolation
- `title`: Task title (string)
- `description`: Optional task description
- `completed`: Boolean indicating completion status
- `created_at`: Timestamp for creation time
- `updated_at`: Timestamp for last update

### New Extension Fields
When adding new fields, use these exact specifications:

- `priority`: Optional[Literal["high", "medium", "low"]] = None (with index)
- `tags`: List[str] = Field(default_factory=list, sa_column=Column(JSON))
- `due_date`: Optional[datetime] = Field(default=None, index=True)
- `recurrence_rule`: Optional[str] = None (RRULE string for recurrence)
- `reminder_enabled`: bool = False (whether to enable reminders)

### SQLModel Best Practices
- Use `Field()` for defaults and indexes: `Field(default=None, index=True)`
- Use `sa_column=Column(JSON)` for complex types like lists
- Import `JSON` from `sqlalchemy` for JSON column type
- Import `Literal` from `typing_extensions` for literal types
- Always include proper type hints
- Add indexes to frequently queried fields (due_date, priority)

## Example Implementation

```python
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, JSON
from typing import List, Optional
from typing_extensions import Literal
from datetime import datetime

class Task(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: int = Field(index=True)  # Preserved for user isolation
    title: str  # Preserved
    description: Optional[str] = None  # Preserved
    completed: bool = False  # Preserved
    created_at: datetime  # Preserved
    updated_at: datetime  # Preserved

    # New extension fields
    priority: Optional[Literal["high", "medium", "low"]] = Field(default=None, index=True)
    tags: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    due_date: Optional[datetime] = Field(default=None, index=True)
    recurrence_rule: Optional[str] = None  # RRULE string
    reminder_enabled: bool = False

    # Relationship back-reference if needed
    user: "User" = Relationship(back_populates="tasks")
```

## Query Patterns

When querying extended Task models, always include user_id filter for security:

```python
# Correct query pattern with user isolation
tasks = session.exec(
    select(Task).where(
        Task.user_id == current_user.id,  # Always include user_id filter
        Task.priority == "high"
    ).order_by(Task.due_date)
).all()

# For due date queries
overdue_tasks = session.exec(
    select(Task).where(
        Task.user_id == current_user.id,  # Always include user_id filter
        Task.due_date < datetime.now(),
        Task.completed == False
    )
).all()
```

## Migration Considerations

- Add new columns with appropriate defaults to maintain backward compatibility
- Create indexes on new indexed fields after adding the columns
- Test existing functionality still works after extensions
- Update any existing Task-related services to handle new fields appropriately
