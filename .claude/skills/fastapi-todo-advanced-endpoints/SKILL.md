---
name: fastapi-todo-advanced-endpoints
description: FastAPI todo advanced endpoints, filter sort recurring due_date tasks query params. Extends existing task endpoints with advanced query parameters for filtering and sorting. Use when implementing enhanced task filtering capabilities with priority, tags, due dates, and recurring tasks.
---

# FastAPI Todo Advanced Endpoints

## Overview

This skill provides guidance for implementing advanced query parameters and endpoints for FastAPI todo applications. It extends existing task endpoints with filtering, sorting, and advanced query capabilities while maintaining security and consistency with existing REST API patterns.

## Advanced Query Parameters

Extend the GET /api/tasks endpoint with these query parameters:

```python
from fastapi import Query
from typing import List, Optional
from datetime import date

# Extended query parameters for advanced filtering
priority: Optional[str] = Query(None, enum=["high", "medium", "low"])
tags: Optional[List[str]] = Query(None)
due_date_before: Optional[date] = Query(None)
sort: Optional[str] = Query(None, enum=["priority", "due_date", "title", "created_at"])
recurring: Optional[bool] = Query(None)
```

### Parameter Details

- `priority`: Filter tasks by priority level (high, medium, low)
- `tags`: Filter tasks by one or more tags (comma-separated values)
- `due_date_before`: Filter tasks with due dates before a specific date
- `sort`: Sort results by specified field (priority, due_date, title, created_at)
- `recurring`: Filter recurring tasks only (true/false)

## Implementation Pattern

### Extended Task Service Methods

```python
from sqlmodel import select
from typing import List
from datetime import date

def get_filtered_tasks(
    session: Session,
    user_id: int,
    priority: Optional[str] = None,
    tags: Optional[List[str]] = None,
    due_date_before: Optional[date] = None,
    sort_field: Optional[str] = None,
    recurring: Optional[bool] = None
) -> List[Task]:
    """
    Get tasks with advanced filtering and sorting capabilities.
    Always enforces user isolation through user_id parameter.
    """
    query = select(Task).where(Task.user_id == user_id)  # User isolation

    # Apply filters
    if priority:
        query = query.where(Task.priority == priority)

    if tags:
        # Assuming tags are stored as JSON and using PostgreSQL
        for tag in tags:
            query = query.where(func.json_contains(Task.tags, tag))

    if due_date_before:
        query = query.where(Task.due_date <= due_date_before)

    if recurring is not None:
        query = query.where(Task.recurrence_rule.is_not(None) == recurring)

    # Apply sorting
    if sort_field == "priority":
        query = query.order_by(Task.priority.desc(), Task.created_at.desc())
    elif sort_field == "due_date":
        query = query.order_by(Task.due_date.asc().nulls_last(), Task.created_at.desc())
    elif sort_field == "title":
        query = query.order_by(Task.title.asc())
    elif sort_field == "created_at":
        query = query.order_by(Task.created_at.desc())
    else:
        # Default ordering
        query = query.order_by(Task.created_at.desc())

    return session.exec(query).all()
```

### Extended API Endpoint

```python
from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from datetime import date
from sqlmodel import Session

@router.get("/", response_model=List[TaskRead])
def list_tasks_advanced(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    priority: Optional[str] = Query(None, enum=["high", "medium", "low"]),
    tags: Optional[List[str]] = Query(None),
    due_date_before: Optional[date] = Query(None),
    sort: Optional[str] = Query(None, enum=["priority", "due_date", "title", "created_at"]),
    recurring: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000)
):
    """
    Get all tasks for the current user with advanced filtering and sorting.
    Implements user isolation by filtering by current user's ID.
    """
    try:
        # Get filtered and sorted tasks for the current user
        tasks = TaskService.get_filtered_tasks(
            session=session,
            user_id=current_user.id,
            priority=priority,
            tags=tags,
            due_date_before=due_date_before,
            sort_field=sort,
            recurring=recurring
        )

        # Apply pagination
        paginated_tasks = tasks[skip:skip+limit]
        return paginated_tasks
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while retrieving tasks"
        )
```

## PATCH Endpoints for Advanced Operations

### Update Recurring Tasks

```python
@router.patch("/{task_id}/recurring", response_model=TaskRead)
def update_task_recurrence(
    task_id: int,
    task_recurrence_update: TaskRecurrenceUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update recurrence settings for a specific task.
    Always verifies user ownership of the task.
    """
    try:
        # Verify user owns the task
        task = TaskService.get_task_by_id(
            session=session,
            task_id=task_id,
            user_id=current_user.id
        )

        # Update recurrence settings
        if task_recurrence_update.recurrence_rule is not None:
            task.recurrence_rule = task_recurrence_update.recurrence_rule

        if task_recurrence_update.recurrence_enabled is not None:
            task.recurrence_enabled = task_recurrence_update.recurrence_enabled

        session.add(task)
        session.commit()
        session.refresh(task)

        return task
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while updating task recurrence"
        )
```

### Update Due Date

```python
@router.patch("/{task_id}/due_date", response_model=TaskRead)
def update_task_due_date(
    task_id: int,
    task_due_date_update: TaskDueDateUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update due date for a specific task.
    Always verifies user ownership of the task.
    """
    try:
        # Verify user owns the task
        task = TaskService.get_task_by_id(
            session=session,
            task_id=task_id,
            user_id=current_user.id
        )

        # Update due date
        task.due_date = task_due_date_update.due_date
        session.add(task)
        session.commit()
        session.refresh(task)

        return task
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while updating task due date"
        )
```

## Pydantic Models for Request/Response

```python
from pydantic import BaseModel
from typing import Optional
from datetime import date

class TaskRecurrenceUpdate(BaseModel):
    recurrence_rule: Optional[str] = None  # RRULE string
    recurrence_enabled: Optional[bool] = None

class TaskDueDateUpdate(BaseModel):
    due_date: Optional[date] = None
```

## Security Considerations

- **User Isolation**: Always filter by `current_user.id` to prevent data leakage
- **Ownership Verification**: Verify user owns the task before any modification
- **Input Validation**: Use Pydantic models and FastAPI Query validators
- **Parameter Sanitization**: Validate enum values and parameter ranges

## Consistency with Existing API

When extending existing endpoints, maintain consistency with the fastapi-todo-rest-api skill by:

- Following the same error handling patterns
- Using the same response models
- Maintaining similar authentication patterns
- Keeping consistent naming conventions
- Following the same validation approaches
