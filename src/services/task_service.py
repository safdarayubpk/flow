from sqlmodel import Session, select
from typing import List, Optional
from datetime import date, datetime
from typing_extensions import Literal
from sqlalchemy import func
from ..models.task import Task, TaskCreate, TaskUpdate, TaskRead
from ..models.user import User


class TaskService:
    """
    Service class for handling advanced task operations including filtering,
    sorting, and managing the extended task fields (priority, tags, due_date, etc.)
    """

    @staticmethod
    def get_filtered_tasks(
        session: Session,
        user_id: str,
        priority: Optional[str] = None,
        tags: Optional[List[str]] = None,
        due_date_before: Optional[date] = None,
        sort_field: Optional[str] = None,
        order: str = "desc",
        recurring: Optional[bool] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """
        Get tasks with advanced filtering and sorting capabilities.
        Always enforces user isolation through user_id parameter.
        """
        query = select(Task).where(Task.user_id == user_id)  # User isolation

        # Apply search filter
        if search:
            search_pattern = f'%{search}%'
            query = query.where(
                Task.title.ilike(search_pattern) |
                Task.description.ilike(search_pattern)
            )

        # Apply filters
        if priority:
            query = query.where(Task.priority == priority)

        if tags:
            # Filter tasks that have any of the specified tags
            # Using a LIKE approach that works across databases including SQLite
            for tag in tags:
                # Searching for the tag in the JSON array string representation
                escaped_tag = tag.replace('"', '""')  # Escape quotes for safety
                query = query.where(Task.tags.like(f'%"{escaped_tag}"%'))

        if due_date_before:
            query = query.where(Task.due_date <= due_date_before)

        if recurring is not None:
            if recurring:
                query = query.where(Task.recurrence_rule.is_not(None))
            else:
                query = query.where(Task.recurrence_rule.is_(None))

        # Apply sorting
        if sort_field == "priority":
            if order == "asc":
                query = query.order_by(Task.priority.asc(), Task.created_at.desc())
            else:  # desc
                query = query.order_by(Task.priority.desc(), Task.created_at.desc())
        elif sort_field == "due_date":
            if order == "asc":
                query = query.order_by(Task.due_date.asc().nulls_last(), Task.created_at.desc())
            else:  # desc
                query = query.order_by(Task.due_date.desc().nulls_last(), Task.created_at.desc())
        elif sort_field == "title":
            if order == "asc":
                query = query.order_by(Task.title.asc())
            else:  # desc
                query = query.order_by(Task.title.desc())
        elif sort_field == "created_at":
            if order == "asc":
                query = query.order_by(Task.created_at.asc())
            else:  # desc
                query = query.order_by(Task.created_at.desc())
        else:
            # Default ordering
            if order == "asc":
                query = query.order_by(Task.created_at.asc())
            else:  # desc
                query = query.order_by(Task.created_at.desc())

        # Apply pagination
        query = query.offset(skip).limit(limit)

        return session.exec(query).all()

    @staticmethod
    def get_active_tasks(session: Session, user_id: str) -> List[Task]:
        """
        Get all active tasks for a specific user (maintains backward compatibility).
        This implements user isolation by filtering by user_id.
        """
        query = select(Task).where(
            Task.user_id == user_id,
            Task.deleted_at.is_(None)  # Only non-deleted tasks
        ).order_by(Task.created_at.desc())

        return session.exec(query).all()

    @staticmethod
    def create_task(session: Session, task_create: TaskCreate, user_id: str) -> Task:
        """
        Create a new task with extended fields.
        """
        task_data = task_create.dict()
        task_data["user_id"] = user_id

        db_task = Task(**task_data)
        session.add(db_task)
        session.commit()
        session.refresh(db_task)

        return db_task

    @staticmethod
    def update_task(session: Session, task_id: int, task_update: TaskUpdate, user_id: str) -> Optional[Task]:
        """
        Update a task with extended fields.
        """
        db_task = session.get(Task, task_id)
        if not db_task or db_task.user_id != user_id:
            return None

        update_data = task_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:  # Only update if the value is not None
                setattr(db_task, field, value)

        session.add(db_task)
        session.commit()
        session.refresh(db_task)

        return db_task

    @staticmethod
    def get_task_by_id(session: Session, task_id: int, user_id: str) -> Optional[Task]:
        """
        Get a specific task by ID for a specific user (enforces user isolation).
        """
        task = session.get(Task, task_id)
        if not task or task.user_id != user_id:
            return None
        return task

    @staticmethod
    def delete_task(session: Session, task_id: int, user_id: str) -> bool:
        """
        Delete a task for a specific user (enforces user isolation).
        """
        db_task = session.get(Task, task_id)
        if not db_task or db_task.user_id != user_id:
            return False

        session.delete(db_task)
        session.commit()
        return True

    @staticmethod
    def get_recurring_tasks(session: Session, user_id: str) -> List[Task]:
        """
        Get all recurring tasks for a specific user.
        """
        query = select(Task).where(
            Task.user_id == user_id,
            Task.recurrence_rule.is_not(None),
            Task.deleted_at.is_(None)
        ).order_by(Task.created_at.desc())

        return session.exec(query).all()

    @staticmethod
    def generate_next_occurrence(task: Task):
        """
        Generate the next occurrence of a recurring task based on the recurrence rule.
        This is a simplified implementation that parses basic RRULE patterns.
        """
        import re
        from datetime import datetime, timedelta

        if not task.recurrence_rule:
            return None

        # Parse the recurrence rule to determine the pattern
        rule_str = task.recurrence_rule.upper()

        # Basic parsing of common RRULE patterns
        if 'FREQ=DAILY' in rule_str:
            interval_match = re.search(r'INTERVAL=(\d+)', rule_str)
            interval = int(interval_match.group(1)) if interval_match else 1
            next_date = (task.due_date or task.created_at) + timedelta(days=interval)
        elif 'FREQ=WEEKLY' in rule_str:
            interval_match = re.search(r'INTERVAL=(\d+)', rule_str)
            interval = int(interval_match.group(1)) if interval_match else 1
            next_date = (task.due_date or task.created_at) + timedelta(weeks=interval)
        elif 'FREQ=MONTHLY' in rule_str:
            # For monthly, we'll add one month (approximately 30 days)
            interval_match = re.search(r'INTERVAL=(\d+)', rule_str)
            interval = int(interval_match.group(1)) if interval_match else 1
            next_date = (task.due_date or task.created_at) + timedelta(days=30*interval)
        elif 'FREQ=YEARLY' in rule_str:
            # For yearly, we'll add 365 days
            interval_match = re.search(r'INTERVAL=(\d+)', rule_str)
            interval = int(interval_match.group(1)) if interval_match else 1
            next_date = (task.due_date or task.created_at) + timedelta(days=365*interval)
        else:
            # Unsupported frequency
            return None

        # Check if there's a COUNT or UNTIL condition
        count_match = re.search(r'COUNT=(\d+)', rule_str)
        if count_match:
            # For simplicity, we won't create more instances if count is reached
            # In a real implementation, we'd track how many instances have been created
            pass

        until_match = re.search(r'UNTIL=([^;]+)', rule_str)
        if until_match:
            until_str = until_match.group(1)
            try:
                # Parse UNTIL date (format: YYYYMMDDTHHMMSSZ)
                if 'T' in until_str:
                    # Handle timezone-aware datetime
                    if len(until_str) >= 16 and until_str[-1] == 'Z':
                        until_date = datetime.strptime(until_str[:-1], '%Y%m%dT%H%M%S')
                    else:
                        until_date = datetime.strptime(until_str, '%Y%m%dT%H%M%S%z').replace(tzinfo=None)
                else:
                    until_date = datetime.strptime(until_str, '%Y%m%d').replace(tzinfo=None)

                if next_date > until_date:
                    return None
            except ValueError:
                # Invalid date format
                pass

        return next_date

    @staticmethod
    def create_recurring_instance(session: Session, original_task: Task, next_due_date: datetime) -> Task:
        """
        Create a new instance of a recurring task with the next due date.
        """
        # Create a copy of the original task with a new due date
        new_task_data = {
            "title": original_task.title,
            "description": original_task.description,
            "priority": original_task.priority,
            "tags": original_task.tags,
            "due_date": next_due_date,
            "recurrence_rule": original_task.recurrence_rule,  # Keep the same recurrence rule
            "reminder_enabled": original_task.reminder_enabled,
            "user_id": original_task.user_id,
            "completed": False  # New instance starts as incomplete
        }

        # Create the new task instance
        new_task = Task(**new_task_data)
        session.add(new_task)
        session.commit()
        session.refresh(new_task)

        return new_task
