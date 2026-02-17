from datetime import datetime, timedelta, timezone
from typing import List, Optional
from sqlmodel import Session, select
from src.models.task import Task
from src.services.task_service import TaskService

# Dapr event publishing (Phase V.3)
from src.services.dapr.publisher import fire_event
from src.services.dapr.events import EventTypes


class RecurringService:
    """
    Service class for handling recurring tasks.
    This implements the recurring task functionality according to ADR-00X.
    """

    @staticmethod
    def process_recurring_tasks(*, session: Session) -> List[Task]:
        """
        Process recurring tasks and create new instances as needed.
        This checks for recurring tasks whose next occurrence is due.
        """
        # Get all active tasks with recurrence rules
        recurring_tasks_query = (
            select(Task)
            .where(Task.recurrence_rule.is_not(None))
            .where(Task.deleted_at.is_(None))
            .where(Task.completed == False)
        )

        recurring_tasks = session.exec(recurring_tasks_query).all()

        # Also check for tasks with reminders that are due
        reminder_tasks_query = (
            select(Task)
            .where(Task.reminder_enabled == True)
            .where(Task.deleted_at.is_(None))
            .where(Task.completed == False)
            .where(Task.due_date.is_not(None))
            .where(Task.due_date <= datetime.now(timezone.utc))
        )
        reminder_tasks = session.exec(reminder_tasks_query).all()

        # Publish reminder-triggered events for due tasks
        for task in reminder_tasks:
            fire_event(
                event_type=EventTypes.REMINDER_TRIGGERED,
                user_id=task.user_id,
                payload={
                    "task_id": task.id,
                    "title": task.title,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                }
            )
            # Disable reminder after triggering to avoid duplicate notifications
            task.reminder_enabled = False
            session.add(task)

        if reminder_tasks:
            session.commit()

        created_tasks = []
        for task in recurring_tasks:
            # Parse the recurrence rule and check if a new task instance should be created
            if RecurringService.should_create_new_instance(task):
                new_task = RecurringService.create_next_instance(
                    session=session,
                    original_task=task
                )
                # Mark original as completed so it isn't rescheduled again
                task.completed = True
                task.updated_at = datetime.now(timezone.utc)
                session.add(task)
                session.commit()

                created_tasks.append(new_task)

        return created_tasks

    @staticmethod
    def should_create_new_instance(task: Task) -> bool:
        """
        Determine if a new instance of a recurring task should be created.
        """
        if not task.recurrence_rule:
            return False

        # For now, implement basic logic - in a real system, you'd parse the rrule string
        # and calculate the next occurrence date
        # This is a simplified implementation
        if task.due_date:
            # Check if due date has passed and task is not completed
            now = datetime.now(timezone.utc)
            if task.due_date < now and not task.completed:
                return True

        return False

    @staticmethod
    def create_next_instance(*, session: Session, original_task: Task) -> Task:
        """
        Create the next instance of a recurring task based on the recurrence rule.
        """
        # Calculate next due date based on recurrence rule
        next_due_date = RecurringService.calculate_next_occurrence(
            original_task.due_date,
            original_task.recurrence_rule
        )

        # Create a new task with the same properties as the original
        from src.models.task import TaskCreate
        new_task_create = TaskCreate(
            title=original_task.title,
            description=original_task.description,
            priority=original_task.priority,
            due_date=next_due_date,
            recurrence_rule=original_task.recurrence_rule
        )

        # Create the new task using the TaskService
        new_task = TaskService.create_task(
            session=session,
            task_create=new_task_create,
            user_id=original_task.user_id
        )

        return new_task

    @staticmethod
    def calculate_next_occurrence(current_date: Optional[datetime], recurrence_rule: str) -> datetime:
        """
        Calculate the next occurrence date based on the current date and recurrence rule.
        This is a simplified implementation - in a real system, you would parse the rrule string.
        """
        if not current_date:
            current_date = datetime.now(timezone.utc)

        # Simplified implementation - in reality, you would parse the rrule string
        # For now, assume different patterns based on the rule content
        if "DAILY" in recurrence_rule.upper() or "INTERVAL=1" in recurrence_rule.upper():
            return current_date + timedelta(days=1)
        elif "WEEKLY" in recurrence_rule.upper() or "INTERVAL=7" in recurrence_rule.upper():
            return current_date + timedelta(weeks=1)
        elif "MONTHLY" in recurrence_rule.upper():
            # Simplified: add ~30 days for monthly
            return current_date + timedelta(days=30)
        elif "YEARLY" in recurrence_rule.upper():
            return current_date + timedelta(days=365)
        else:
            # Default: daily
            return current_date + timedelta(days=1)