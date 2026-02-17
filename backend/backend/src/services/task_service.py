from sqlmodel import Session, select, desc
from fastapi import HTTPException, status
from typing import List, Optional, Dict
from src.models.task import Task, TaskCreate, TaskUpdate
from src.models.tag import Tag
from src.models.task_tag_link import TaskTagLink
from src.models.user import User
from src.core.isolation import ensure_user_owns_resource, get_user_resources
from datetime import datetime

# Dapr event publishing (Phase V.3)
from src.services.dapr.publisher import fire_event
from src.services.dapr.events import EventTypes


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
            reminder_enabled=task_create.reminder_enabled,
            user_id=user_id
        )

        session.add(db_task)
        session.commit()
        session.refresh(db_task)

        # Publish task-created event (fire-and-forget)
        fire_event(
            event_type=EventTypes.TASK_CREATED,
            user_id=user_id,
            payload={
                "task_id": db_task.id,
                "title": db_task.title,
                "priority": db_task.priority,
                "tags": [],  # Tags linked separately
                "due_date": db_task.due_date.isoformat() if db_task.due_date else None,
            }
        )

        # If recurring task, also publish recurring-task-created event
        if db_task.recurrence_rule:
            fire_event(
                event_type=EventTypes.RECURRING_TASK_CREATED,
                user_id=user_id,
                payload={
                    "task_id": db_task.id,
                    "title": db_task.title,
                    "recurrence_rule": db_task.recurrence_rule,
                }
            )

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

        # Remove tags from direct field update (handled separately via TaskTagLink)
        update_data.pop("tags", None)

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

        # Publish task-updated event (fire-and-forget)
        if update_data:  # Only publish if there were actual changes
            fire_event(
                event_type=EventTypes.TASK_UPDATED,
                user_id=user_id,
                payload={
                    "task_id": task.id,
                    "changes": update_data,
                }
            )

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

        # Publish task-deleted event (fire-and-forget)
        fire_event(
            event_type=EventTypes.TASK_DELETED,
            user_id=user_id,
            payload={
                "task_id": task_id,
            }
        )

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

        # Publish task-completed event only when task is marked as completed
        if task.completed:
            fire_event(
                event_type=EventTypes.TASK_COMPLETED,
                user_id=user_id,
                payload={
                    "task_id": task.id,
                }
            )

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

    @staticmethod
    def resolve_and_link_tags(*, session: Session, task_id: int, user_id: str, tag_names: List[str]) -> None:
        """
        Resolve tag names to Tag records (get-or-create) and create TaskTagLink entries.
        Replaces all existing tag associations for the task.
        """
        # Remove existing links for this task
        existing_links = session.exec(
            select(TaskTagLink).where(TaskTagLink.task_id == task_id)
        ).all()
        for link in existing_links:
            session.delete(link)

        # For each tag name, find or create the tag, then link it
        for tag_name in tag_names:
            tag_name = tag_name.strip()
            if not tag_name:
                continue

            # Find existing tag for this user
            tag = session.exec(
                select(Tag).where(Tag.name == tag_name, Tag.user_id == user_id)
            ).first()

            # Create tag if it doesn't exist
            if not tag:
                tag = Tag(name=tag_name, user_id=user_id)
                session.add(tag)
                session.flush()  # Get the tag ID

            # Create the link
            link = TaskTagLink(task_id=task_id, tag_id=tag.id)
            session.add(link)

        session.commit()

    @staticmethod
    def get_task_tag_names(*, session: Session, task_id: int) -> List[str]:
        """Get list of tag names for a specific task."""
        tags = session.exec(
            select(Tag.name)
            .join(TaskTagLink, Tag.id == TaskTagLink.tag_id)
            .where(TaskTagLink.task_id == task_id)
        ).all()
        return list(tags)

    @staticmethod
    def get_tasks_tag_names_batch(*, session: Session, task_ids: List[int]) -> Dict[int, List[str]]:
        """Get tag names for multiple tasks in a single query."""
        if not task_ids:
            return {}

        results = session.exec(
            select(TaskTagLink.task_id, Tag.name)
            .join(Tag, Tag.id == TaskTagLink.tag_id)
            .where(TaskTagLink.task_id.in_(task_ids))
        ).all()

        tag_map: Dict[int, List[str]] = {tid: [] for tid in task_ids}
        for task_id, tag_name in results:
            tag_map[task_id].append(tag_name)

        return tag_map

    @staticmethod
    def enrich_task_response(task: Task, tags: List[str]) -> dict:
        """Convert a Task ORM object + tag names into a dict suitable for TaskRead."""
        data = {
            "id": task.id,
            "user_id": task.user_id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "priority": task.priority,
            "due_date": task.due_date,
            "recurrence_rule": task.recurrence_rule,
            "reminder_enabled": task.reminder_enabled,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
            "deleted_at": task.deleted_at,
            "tags": tags,
        }
        return data