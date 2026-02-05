from sqlmodel import Session, select, desc
from fastapi import HTTPException, status
from typing import List, Optional
from src.models.task import Task, TaskCreate, TaskUpdate
from src.models.user import User
from src.core.isolation import ensure_user_owns_resource, get_user_resources
from datetime import datetime


class TaskService:
    """
    Service class for task-related operations with user isolation enforcement.
    This implements ADR-002 for application-level user isolation.
    """

    @staticmethod
    def create_task(*, session: Session, task_create: TaskCreate, user_id: str) -> Task:
        """
        Create a new task with the provided details and assign it to the user.
        This implements user isolation by assigning the task to the current user.
        """
        # Create new task with user_id assignment
        db_task = Task(
            title=task_create.title,
            description=task_create.description,
            completed=task_create.completed or False,
            priority=task_create.priority,
            due_date=task_create.due_date,
            recurrence_rule=task_create.recurrence_rule,
            user_id=user_id
        )

        session.add(db_task)
        session.commit()
        session.refresh(db_task)

        return db_task

    @staticmethod
    def get_user_tasks(*, session: Session, user_id: str) -> List[Task]:
        """
        Get all tasks that belong to the specified user.
        This implements ADR-002 for application-level user isolation by filtering by user_id.
        """
        # Use the isolation helper to get user's resources
        return get_user_resources(session, Task, user_id)

    @staticmethod
    def get_task_by_id(*, session: Session, task_id: int, user_id: str) -> Task:
        """
        Get a specific task by ID, ensuring it belongs to the user.
        This implements ADR-002 for application-level user isolation.
        """
        # Use the isolation helper to ensure user owns the resource
        return ensure_user_owns_resource(session, Task, task_id, user_id)

    @staticmethod
    def update_task(*, session: Session, task_id: int, task_update: TaskUpdate, user_id: str) -> Task:
        """
        Update a task, ensuring it belongs to the user.
        This implements ADR-002 for application-level user isolation.
        """
        # First, verify that the user owns this task
        task = ensure_user_owns_resource(session, Task, task_id, user_id)

        # Update only the fields that are provided
        update_data = task_update.dict(exclude_unset=True)

        # Handle soft delete - if a task is "deleted", set the deleted_at timestamp
        if update_data.get("deleted_at"):
            update_data["deleted_at"] = datetime.utcnow()

        # Update the task with the new data
        for field, value in update_data.items():
            setattr(task, field, value)

        # Update the updated_at timestamp
        task.updated_at = datetime.utcnow()

        session.add(task)
        session.commit()
        session.refresh(task)

        return task

    @staticmethod
    def delete_task(*, session: Session, task_id: int, user_id: str) -> bool:
        """
        Delete a task (soft delete per ADR-003), ensuring it belongs to the user.
        This implements ADR-002 for application-level user isolation and ADR-003 for soft delete.
        """
        # First, verify that the user owns this task
        task = ensure_user_owns_resource(session, Task, task_id, user_id)

        # Perform soft delete by setting the deleted_at timestamp
        task.deleted_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()

        session.add(task)
        session.commit()

        return True

    @staticmethod
    def toggle_task_completion(*, session: Session, task_id: int, user_id: str) -> Task:
        """
        Toggle the completion status of a task, ensuring it belongs to the user.
        This implements ADR-002 for application-level user isolation.
        """
        # First, verify that the user owns this task
        task = ensure_user_owns_resource(session, Task, task_id, user_id)

        # Toggle the completion status
        task.completed = not task.completed
        task.updated_at = datetime.utcnow()

        session.add(task)
        session.commit()
        session.refresh(task)

        return task

    @staticmethod
    def get_active_tasks(*, session: Session, user_id: str) -> List[Task]:
        """
        Get all active (non-deleted) tasks that belong to the specified user.
        This implements ADR-003 for soft delete by filtering out deleted tasks.
        """
        # Get all tasks for the user
        all_tasks = get_user_resources(session, Task, user_id)

        # Filter out soft-deleted tasks
        active_tasks = [task for task in all_tasks if task.deleted_at is None]

        # Sort by creation date (newest first)
        active_tasks.sort(key=lambda x: x.created_at, reverse=True)

        return active_tasks

    @staticmethod
    def get_filtered_tasks(
        *,
        session: Session,
        user_id: str,
        priority: Optional[str] = None,
        due_date_before: Optional[datetime.date] = None,
        sort_field: Optional[str] = "created_at",
        order: Optional[str] = "desc",
        recurring: Optional[bool] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """
        Get tasks with advanced filtering and sorting options.
        This implements ADR-002 for user isolation by filtering by user_id.
        """
        # Build the query with user isolation
        query = select(Task).where(Task.user_id == user_id, Task.deleted_at.is_(None))

        # Apply filters
        if priority:
            query = query.where(Task.priority == priority)

        if due_date_before:
            from datetime import datetime
            # Convert date to datetime for comparison (end of day)
            due_date_end = datetime.combine(due_date_before, datetime.max.time())
            query = query.where(Task.due_date <= due_date_end)

        if recurring is not None:
            if recurring:
                query = query.where(Task.recurrence_rule.is_not(None))
            else:
                query = query.where(Task.recurrence_rule.is_(None))

        if search:
            search_lower = f"%{search.lower()}%"
            from sqlalchemy import or_
            query = query.where(
                or_(
                    Task.title.ilike(search_lower),
                    Task.description.ilike(search_lower) if Task.description is not None else False
                )
            )

        # Apply sorting
        sort_columns = {
            "priority": Task.priority,
            "due_date": Task.due_date,
            "title": Task.title,
            "created_at": Task.created_at
        }

        if sort_field in sort_columns:
            if order == "desc":
                query = query.order_by(desc(sort_columns[sort_field]))
            else:
                query = query.order_by(sort_columns[sort_field])

        # Apply pagination
        query = query.offset(skip).limit(limit)

        # Execute query
        tasks = session.exec(query).all()

        return tasks