# FastAPI Todo Advanced Endpoints API Reference

This document provides detailed reference information for implementing advanced query parameters and endpoints for FastAPI todo applications.

## Query Parameter Specifications

### Filtering Parameters

#### Priority Filter
```python
from fastapi import Query
from typing import Optional

priority: Optional[str] = Query(
    None,
    enum=["high", "medium", "low"],
    description="Filter tasks by priority level"
)
```

- **Type**: Optional string with enum values
- **Valid values**: "high", "medium", "low"
- **Default**: None (no filtering)
- **Description**: Filters tasks based on their priority level

#### Tags Filter
```python
from fastapi import Query
from typing import List, Optional

tags: Optional[List[str]] = Query(
    None,
    description="Filter tasks by one or more tags"
)
```

- **Type**: Optional list of strings
- **Format**: Comma-separated values (e.g., ?tags=work,urgent,personal)
- **Default**: None (no filtering)
- **Description**: Filters tasks that contain any of the specified tags

#### Due Date Filter
```python
from fastapi import Query
from typing import Optional
from datetime import date

due_date_before: Optional[date] = Query(
    None,
    description="Filter tasks with due dates before this date"
)
```

- **Type**: Optional date
- **Format**: ISO 8601 date format (YYYY-MM-DD)
- **Default**: None (no filtering)
- **Description**: Filters tasks with due dates before or equal to the specified date

#### Recurring Filter
```python
from fastapi import Query
from typing import Optional

recurring: Optional[bool] = Query(
    None,
    description="Filter recurring tasks only"
)
```

- **Type**: Optional boolean
- **Default**: None (no filtering)
- **Description**: When true, returns only recurring tasks; when false, returns only non-recurring tasks

### Sorting Parameters

#### Sort Parameter
```python
from fastapi import Query
from typing import Optional

sort: Optional[str] = Query(
    None,
    enum=["priority", "due_date", "title", "created_at"],
    description="Sort results by specified field"
)
```

- **Type**: Optional string with enum values
- **Valid values**: "priority", "due_date", "title", "created_at"
- **Default**: None (default ordering)
- **Description**: Specifies the field to sort results by

### Pagination Parameters
```python
from fastapi import Query

skip: int = Query(
    0,
    ge=0,
    description="Number of items to skip for pagination"
)
limit: int = Query(
    100,
    le=1000,
    ge=1,
    description="Maximum number of items to return"
)
```

- **skip**: Number of items to skip (default: 0, minimum: 0)
- **limit**: Maximum number of items to return (default: 100, maximum: 1000)

## Database Query Implementation

### Advanced Filtering with SQLModel

```python
from sqlmodel import select, Session
from typing import List, Optional
from datetime import date

def get_filtered_tasks(
    session: Session,
    user_id: int,
    priority: Optional[str] = None,
    tags: Optional[List[str]] = None,
    due_date_before: Optional[date] = None,
    sort_field: Optional[str] = None,
    recurring: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Task]:
    """
    Advanced task filtering with all parameters.
    Always enforces user isolation through user_id.
    """
    query = select(Task).where(Task.user_id == user_id)

    # Apply priority filter
    if priority:
        query = query.where(Task.priority == priority)

    # Apply tags filter
    if tags:
        # For JSON field - PostgreSQL specific
        for tag in tags:
            query = query.where(func.json_contains(Task.tags, tag))

    # Apply due date filter
    if due_date_before:
        query = query.where(Task.due_date <= due_date_before)

    # Apply recurring filter
    if recurring is not None:
        if recurring:
            query = query.where(Task.recurrence_rule.is_not(None))
        else:
            query = query.where(Task.recurrence_rule.is_(None))

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
        query = query.order_by(Task.created_at.desc())

    # Apply pagination
    query = query.offset(skip).limit(limit)

    return session.exec(query).all()
```

## PATCH Endpoint Implementations

### Update Recurring Task Properties

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

@router.patch("/{task_id}/recurring", response_model=TaskRead)
def update_task_recurrence(
    task_id: int,
    task_recurrence_update: TaskRecurrenceUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update recurrence properties for a specific task.
    Verifies user ownership before modification.
    """
    # Get the task and verify ownership
    task = session.get(Task, task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Update recurrence properties
    if task_recurrence_update.recurrence_rule is not None:
        task.recurrence_rule = task_recurrence_update.recurrence_rule

    if task_recurrence_update.recurrence_enabled is not None:
        task.recurrence_enabled = task_recurrence_update.recurrence_enabled

    # Update timestamps
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    return task
```

### Update Task Due Date

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
    Verifies user ownership before modification.
    """
    # Get the task and verify ownership
    task = session.get(Task, task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Update due date
    task.due_date = task_due_date_update.due_date
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    return task
```

## Pydantic Models

### Request Models

```python
from pydantic import BaseModel
from typing import Optional
from datetime import date

class TaskRecurrenceUpdate(BaseModel):
    """Request model for updating task recurrence properties"""
    recurrence_rule: Optional[str] = None  # RRULE string for recurrence pattern
    recurrence_enabled: Optional[bool] = None  # Whether recurrence is enabled

class TaskDueDateUpdate(BaseModel):
    """Request model for updating task due date"""
    due_date: Optional[date] = None  # New due date for the task
```

## Security Implementation

### User Isolation Enforcement

All endpoints must enforce user isolation by:

1. Using authentication dependency:
```python
current_user: User = Depends(get_current_user)
```

2. Filtering by user ID in queries:
```python
query = select(Task).where(Task.user_id == current_user.id)
```

3. Verifying ownership before modifications:
```python
task = session.get(Task, task_id)
if not task or task.user_id != current_user.id:
    raise HTTPException(status_code=404, detail="Task not found")
```

## Error Handling

### Standard Error Responses

- **400 Bad Request**: Invalid query parameters or request body
- **401 Unauthorized**: Missing or invalid authentication
- **403 Forbidden**: User not authorized to access the resource
- **404 Not Found**: Task does not exist or does not belong to user
- **500 Internal Server Error**: Unexpected server error

### Error Response Format

```json
{
    "detail": "Descriptive error message"
}
```
