---
name: user-isolation-enforcer
description: enforce user isolation, filter by user_id, prevent data leak in query, multi-user task filter, always add WHERE user_id
---

# User Isolation Enforcer

## Overview

This skill enforces user isolation in database queries by ensuring every query involving user data includes proper user_id filtering. It prevents data leaks by mandating WHERE clauses that restrict results to the current authenticated user.

## Core Enforcement Rule

**In EVERY database query involving tasks or user-related data, automatically add the filter:**
```python
.where(Model.user_id == current_user.id)
```

## SQLModel Query Pattern

Use this pattern for all database operations:

```python
from sqlmodel import select
from your_models import Task

# CORRECT - Includes user_id filter
results = session.exec(
    select(Task)
    .where(Task.user_id == current_user.id)
).all()

# INCORRECT - Missing user_id filter (will cause data leak)
results = session.exec(select(Task)).all()  # DON'T DO THIS
```

## Required Query Patterns

### List Operations
```python
def list_user_tasks(session, current_user):
    return session.exec(
        select(Task)
        .where(Task.user_id == current_user.id)
    ).all()
```

### Get Operations
```python
def get_user_task(session, task_id, current_user):
    return session.exec(
        select(Task)
        .where(Task.user_id == current_user.id)
        .where(Task.id == task_id)
    ).first()
```

### Update Operations
```python
def update_user_task(session, task_id, update_data, current_user):
    task = session.exec(
        select(Task)
        .where(Task.user_id == current_user.id)
        .where(Task.id == task_id)
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update task...
    session.add(task)
    session.commit()
```

### Delete Operations
```python
def delete_user_task(session, task_id, current_user):
    task = session.exec(
        select(Task)
        .where(Task.user_id == current_user.id)
        .where(Task.id == task_id)
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    session.delete(task)
    session.commit()
```

## Security Warning

⚠️ **Data leak here would violate multi-user isolation** - Always verify that every query includes proper user_id filtering to prevent unauthorized access to other users' data.

## Enforcement Checklist

Before executing any database query:
- [ ] Verify WHERE clause includes `Model.user_id == current_user.id`
- [ ] Confirm current_user context is properly extracted from JWT
- [ ] Test that query returns only data owned by current user
- [ ] Ensure no JOINs inadvertently expose other users' data

## Violation Detection

If you see code without proper user filtering:
1. **Warning**: "Missing user_id filter - this could cause data leak"
2. **Correction**: Add `.where(Model.user_id == current_user.id)` to the query
3. **Verification**: Test that user A cannot access user B's data

## Critical Reminder

**Never return data from other users** - Every query must be scoped to the current authenticated user to maintain proper multi-user isolation.
