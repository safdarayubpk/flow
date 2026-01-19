---
name: sqlmodel-todo-task-model
description: todo task sqlmodel, task database model, sqlmodel task schema with user_id, create todo model
---

# SQLModel Todo Task Model

## Overview

This skill provides the standardized SQLModel Task class for Todo applications with proper user isolation. It enforces multi-user isolation via user_id and includes all required fields for a complete Todo task management system.

## Core Task Model

### Standard Task Class Definition
Use this exact SQLModel Task class unless explicitly overridden:

```python
from sqlmodel import SQLModel, Field, Column
from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime


class Task(SQLModel, table=True):
    # Enforces multi-user isolation via user_id
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)  # Foreign key to user, indexed for performance
    title: str = Field(max_length=200)  # Required, max_length=200
    description: Optional[str] = None
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), onupdate=datetime.utcnow))
```

## Field Specifications

### Required Fields
- `id: Optional[int] = Field(default=None, primary_key=True)`
- `user_id: str` - Foreign key to user, indexed for performance
- `title: str` - Required field with max_length=200

### Optional Fields
- `description: Optional[str] = None`
- `completed: bool = Field(default=False)` - Tracks task completion status
- `created_at: datetime = Field(default_factory=datetime.utcnow)` - Timestamp of creation
- `updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), onupdate=datetime.utcnow))` - Timestamp of last update

## Indexing Strategy

Always include indexes for performance:
- Index on `user_id` for efficient multi-user filtering
- Index on `completed` for status-based queries

## Relationship Pattern

When defining relationships with User model:

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime


class Task(SQLModel, table=True):
    # Enforces multi-user isolation via user_id
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, foreign_key="user.id")
    title: str = Field(max_length=200)
    description: Optional[str] = None
    completed: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), onupdate=datetime.utcnow))

    # Relationship to User if needed
    # user: "User" = Relationship(back_populates="tasks")
```

## Multi-User Isolation Enforcement

⚠️ **Critical**: The `user_id` field is essential for enforcing multi-user isolation. Every database query must filter by `user_id` to prevent data leakage between users.

Example query pattern:
```python
from sqlmodel import select

# Correct - includes user_id filter
user_tasks = session.exec(
    select(Task)
    .where(Task.user_id == current_user.id)
).all()
```

## Validation Checklist

Before implementing the Task model:
- [ ] Uses SQLModel with table=True
- [ ] Includes id field with primary_key=True
- [ ] Includes user_id field with index for multi-user isolation
- [ ] Title has max_length=200 constraint
- [ ] Completed field has index for performance
- [ ] Has both created_at and updated_at timestamps
- [ ] Updated_at field has onupdate trigger
- [ ] Comment "# Enforces multi-user isolation via user_id" is included