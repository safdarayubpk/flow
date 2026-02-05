---
name: fastapi-todo-rest-api
description: todo rest endpoint, /api/tasks crud, fastapi todo api route, patch /complete endpoint, todo specific rest api
---

# FastAPI Todo REST API

## Overview

This skill provides standardized REST API endpoints for Todo applications using FastAPI. It enforces proper user isolation, correct HTTP methods, status codes, and follows the exact endpoint patterns required for Todo task management.

## Required Endpoint Patterns

### Standard Todo API Routes
Always use these exact endpoint patterns for Todo app:

- **GET**    `/api/tasks`              → list current user's tasks (with optional ?status= & ?sort=)
- **POST**   `/api/tasks`              → create new task (body: title + description)
- **GET**    `/api/tasks/{task_id}`    → get single task (check ownership)
- **PUT**    `/api/tasks/{task_id}`    → full update
- **PATCH**  `/api/tasks/{task_id}/complete` → toggle completed status
- **DELETE** `/api/tasks/{task_id}`    → delete task

## API Router Setup

### Router Configuration
Use APIRouter with the correct prefix:

```python
from fastapi import APIRouter

router = APIRouter(prefix="/api/tasks")
```

## Endpoint Implementation

### GET /api/tasks - List Tasks

```python
from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from your_models import TaskRead
from your_auth import get_current_user, CurrentUser

router = APIRouter(prefix="/api/tasks")

@router.get("", response_model=List[TaskRead])
async def list_tasks(
    current_user: CurrentUser = Depends(get_current_user),
    status: Optional[str] = Query(None, description="Filter by status: pending, completed, all"),
    sort: Optional[str] = Query("created", description="Sort by: created, title, due_date")
):
    # Implementation here - filter by current_user.id
    pass
```

### POST /api/tasks - Create Task

```python
from fastapi import status

@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_create: TaskCreate,
    current_user: CurrentUser = Depends(get_current_user)
):
    # Implementation here - assign current_user.id to user_id
    pass
```

### GET /api/tasks/{task_id} - Get Single Task

```python
@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: int,
    current_user: CurrentUser = Depends(get_current_user)
):
    # Implementation here - verify task belongs to current_user
    pass
```

### PUT /api/tasks/{task_id} - Update Task

```python
@router.put("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: CurrentUser = Depends(get_current_user)
):
    # Implementation here - verify task belongs to current_user
    pass
```

### PATCH /api/tasks/{task_id}/complete - Toggle Completion

```python
@router.patch("/{task_id}/complete", response_model=TaskRead)
async def toggle_task_completion(
    task_id: int,
    current_user: CurrentUser = Depends(get_current_user)
):
    # Implementation here - verify task belongs to current_user and toggle completion
    pass
```

### DELETE /api/tasks/{task_id} - Delete Task

```python
from fastapi import status

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: CurrentUser = Depends(get_current_user)
):
    # Implementation here - verify task belongs to current_user and delete
    pass
```

## Authentication Requirements

### JWT User Dependency
Always depend on current_user from JWT dependency:

```python
from your_auth import get_current_user, CurrentUser

# Use in every endpoint:
current_user: CurrentUser = Depends(get_current_user)
```

## Response Models

### Pydantic Response Models
Always return Pydantic response models:

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False

class TaskCreate(TaskBase):
    pass

class TaskUpdate(TaskBase):
    pass

class TaskRead(TaskBase):
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

## HTTP Status Codes

### Correct Status Code Usage
- **200 OK**: Successful GET requests
- **201 CREATED**: Successful POST requests
- **204 NO CONTENT**: Successful DELETE requests
- **400 BAD REQUEST**: Invalid input/data
- **401 UNAUTHORIZED**: Invalid/missing authentication
- **403 FORBIDDEN**: Access denied (user isolation violation)
- **404 NOT FOUND**: Resource not found
- **422 UNPROCESSABLE ENTITY**: Validation errors

## User Isolation Enforcement

⚠️ **Critical**: Never expose other users' data. Always verify that requested task belongs to current_user before performing operations.

Example verification pattern:
```python
task = session.exec(
    select(Task)
    .where(Task.id == task_id)
    .where(Task.user_id == current_user.id)
).first()

if not task:
    raise HTTPException(status_code=404, detail="Task not found")
```

## Validation Checklist

Before implementing any Todo API endpoint:
- [ ] Uses correct endpoint pattern as specified
- [ ] APIRouter has prefix="/api/tasks"
- [ ] Depends on current_user from JWT dependency
- [ ] Returns appropriate Pydantic response models
- [ ] Uses correct HTTP status codes
- [ ] Includes user isolation verification
- [ ] Validates that user can only access their own tasks
- [ ] Implements proper error handling
