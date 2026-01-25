from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlmodel import Session
from typing import List
from src.services.task_service import TaskService
from src.core.database import get_session
from src.core.auth import get_current_user
from src.models.task import Task, TaskCreate, TaskUpdate, TaskRead
from src.models.user import User
from datetime import datetime


router = APIRouter()


@router.get("/", response_model=List[TaskRead])
def list_tasks(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    """
    Get all tasks for the current user.
    This implements ADR-002 for user isolation by filtering by current user's ID.
    """
    try:
        # Get only active (non-deleted) tasks for the current user
        tasks = TaskService.get_active_tasks(session=session, user_id=current_user.id)
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