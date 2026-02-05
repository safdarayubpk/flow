from datetime import datetime, timedelta
from typing import List, Optional
from sqlmodel import Session
from src.models.task import Task
from src.services.task_service import TaskService


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

        from sqlmodel import select
        recurring_tasks = session.exec(recurring_tasks_query).all()

        created_tasks = []
        for task in recurring_tasks:
            # Parse the recurrence rule and check if a new task instance should be created
            if RecurringService.should_create_new_instance(task):
                new_task = RecurringService.create_next_instance(
                    session=session,
                    original_task=task
                )
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
            now = datetime.utcnow()
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
            current_date = datetime.utcnow()

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