from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from sqlmodel import Session
from typing import List, Optional
from src.services.task_service import TaskService
from src.core.database import get_session
from src.core.auth import get_current_user
from src.models.task import Task, TaskCreate, TaskUpdate, TaskRead
from src.models.user import User
from datetime import datetime, date


router = APIRouter()


@router.get("/", response_model=List[TaskRead])
def list_tasks_advanced(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    priority: Optional[str] = Query(None, regex=r"^(high|medium|low)$"),
    due_date_before: Optional[date] = Query(None),
    sort: Optional[str] = Query(None, regex=r"^(priority|due_date|title|created_at)$"),
    order: Optional[str] = Query("desc", regex=r"^(asc|desc)$"),
    recurring: Optional[bool] = Query(None),
    search: Optional[str] = Query(None, description="Search keyword for title and description"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000)
):
    """
    Get all tasks for the current user with advanced filtering and sorting.
    This implements ADR-002 for user isolation by filtering by current user's ID.
    """
    try:
        # Get tasks with advanced filtering and sorting for the current user
        tasks = TaskService.get_filtered_tasks(
            session=session,
            user_id=current_user.id,
            priority=priority,
            due_date_before=due_date_before,
            sort_field=sort,
            order=order,
            recurring=recurring,
            search=search,
            skip=skip,
            limit=limit
        )
        return tasks
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while retrieving tasks"
        )


@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(
    task_create: TaskCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Create a new task for the current user.
    This implements user isolation by assigning the task to the current user.
    """
    try:
        # Validate task title length per spec (1-200 characters)
        if len(task_create.title.strip()) < 1 or len(task_create.title) > 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task title must be between 1 and 200 characters"
            )

        # Create task with user_id assignment
        task = TaskService.create_task(
            session=session,
            task_create=task_create,
            user_id=current_user.id
        )
        return task
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while creating the task"
        )


@router.get("/{task_id}", response_model=TaskRead)
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get a specific task by ID if it belongs to the current user.
    This implements ADR-002 for user isolation by validating ownership.
    """
    try:
        task = TaskService.get_task_by_id(
            session=session,
            task_id=task_id,
            user_id=current_user.id
        )

        # Check if task is soft-deleted
        if task.deleted_at:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        return task
    except HTTPException:
        # Re-raise HTTP exceptions (like 404 for not found)
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while retrieving the task"
        )


@router.put("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update an existing task if it belongs to the current user.
    This implements ADR-002 for user isolation by validating ownership.
    """
    try:
        # Validate task title length if it's being updated
        if task_update.title is not None:
            if len(task_update.title.strip()) < 1 or len(task_update.title) > 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Task title must be between 1 and 200 characters"
                )

        task = TaskService.update_task(
            session=session,
            task_id=task_id,
            task_update=task_update,
            user_id=current_user.id
        )
        return task
    except HTTPException:
        # Re-raise HTTP exceptions (like 404 for not found, 403 for forbidden)
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while updating the task"
        )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete a task if it belongs to the current user.
    This implements ADR-003 for soft delete strategy.
    """
    try:
        # Verify user owns the task before deletion
        task = TaskService.get_task_by_id(
            session=session,
            task_id=task_id,
            user_id=current_user.id
        )

        # Perform soft delete
        success = TaskService.delete_task(
            session=session,
            task_id=task_id,
            user_id=current_user.id
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Return 204 No Content for successful deletion
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException:
        # Re-raise HTTP exceptions (like 404 for not found, 403 for forbidden)
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while deleting the task"
        )


@router.patch("/{task_id}/complete", response_model=TaskRead)
def toggle_task_completion(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Toggle the completion status of a task if it belongs to the current user.
    This implements ADR-002 for user isolation by validating ownership.
    """
    try:
        task = TaskService.toggle_task_completion(
            session=session,
            task_id=task_id,
            user_id=current_user.id
        )
        return task
    except HTTPException:
        # Re-raise HTTP exceptions (like 404 for not found, 403 for forbidden)
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while toggling task completion"
        )


@router.patch("/{task_id}/recurring", response_model=TaskRead)
def update_task_recurring(
    task_id: int,
    rrule_string: str = Query(..., description="RFC 5545 recurrence rule string"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update the recurring pattern of a task if it belongs to the current user.
    This implements ADR-002 for user isolation by validating ownership.
    """
    try:
        # Validate rrule_string format (basic validation)
        if not rrule_string or not isinstance(rrule_string, str) or len(rrule_string) < 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid rrule string format"
            )

        # Verify user owns the task before updating
        task = TaskService.get_task_by_id(
            session=session,
            task_id=task_id,
            user_id=current_user.id
        )

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found or does not belong to current user"
            )

        # Update the task with recurrence rule
        from src.models.task import TaskUpdate
        task_update = TaskUpdate(recurrence_rule=rrule_string)
        updated_task = TaskService.update_task(
            session=session,
            task_id=task_id,
            task_update=task_update,
            user_id=current_user.id
        )

        return updated_task
    except HTTPException:
        # Re-raise HTTP exceptions (like 404 for not found, 403 for forbidden)
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while updating task recurring pattern"
        )


@router.patch("/{task_id}/due_date", response_model=TaskRead)
def update_task_due_date(
    task_id: int,
    due_date: str = Query(..., description="Due date in ISO format: YYYY-MM-DDTHH:MM:SSZ"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update the due date of a task if it belongs to the current user.
    This implements ADR-002 for user isolation by validating ownership.
    """
    try:
        from datetime import datetime

        # Validate due_date format
        try:
            parsed_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use ISO format: YYYY-MM-DDTHH:MM:SSZ"
            )

        # Verify user owns the task before updating
        task = TaskService.get_task_by_id(
            session=session,
            task_id=task_id,
            user_id=current_user.id
        )

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found or does not belong to current user"
            )

        # Update the task with due date
        from src.models.task import TaskUpdate
        task_update = TaskUpdate(due_date=parsed_date)
        updated_task = TaskService.update_task(
            session=session,
            task_id=task_id,
            task_update=task_update,
            user_id=current_user.id
        )

        return updated_task
    except HTTPException:
        # Re-raise HTTP exceptions (like 404 for not found, 403 for forbidden)
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while updating task due date"
        )