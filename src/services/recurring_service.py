from sqlmodel import Session
from datetime import datetime, timedelta
from typing import List
from ..models.task import Task
from .task_service import TaskService


class RecurringTaskService:
    """
    Service class for handling recurring task management and instance generation.
    """

    @staticmethod
    def process_recurring_tasks(session: Session, user_id: str):
        """
        Process all recurring tasks for a user and create new instances if needed.
        This should be called periodically (e.g., daily) to generate new task instances.
        """
        # Get all recurring tasks for the user
        recurring_tasks = TaskService.get_recurring_tasks(session, user_id)

        for task in recurring_tasks:
            # Generate the next occurrence based on the recurrence rule
            next_date = TaskService.generate_next_occurrence(task)

            if next_date and next_date.date() >= datetime.now().date():
                # Check if an instance already exists for this date
                existing_instance = RecurringTaskService._check_existing_instance(
                    session, task.id, next_date, user_id
                )

                if not existing_instance:
                    # Create a new instance of the recurring task
                    new_task = TaskService.create_recurring_instance(
                        session, task, next_date
                    )

    @staticmethod
    def _check_existing_instance(session: Session, original_task_id: int, due_date: datetime, user_id: str) -> bool:
        """
        Check if a recurring task instance already exists for the given date.
        This prevents duplicate instances from being created.
        """
        from sqlmodel import select
        from ..models.task import Task

        # Look for tasks with the same title and close due date
        # In a more sophisticated system, we might track recurring task instances differently
        query = select(Task).where(
            Task.user_id == user_id,
            Task.title == f"{original_task_id}_instance_{due_date.strftime('%Y-%m-%d')}",
            Task.due_date == due_date
        )

        # For now, we'll check if there's a task with similar characteristics
        # In practice, we might need to implement a more robust way to track recurring instances
        # based on the original task ID and date
        existing_tasks = session.exec(query).all()
        return len(existing_tasks) > 0

    @staticmethod
    def validate_rrule(rrule_string: str) -> bool:
        """
        Validate that the RRULE string follows basic RFC 5545 format.
        """
        if not rrule_string or not isinstance(rrule_string, str):
            return False

        # Basic validation - should contain FREQ=
        if 'FREQ=' not in rrule_string.upper():
            return False

        # Extract frequency
        freq_parts = rrule_string.upper().split('FREQ=')
        if len(freq_parts) < 2:
            return False

        freq_part = freq_parts[1].split(';')[0]
        valid_freqs = ['DAILY', 'WEEKLY', 'MONTHLY', 'YEARLY']

        if freq_part not in valid_freqs:
            return False

        return True

    @staticmethod
    def create_recurring_series(session: Session, task_template: Task, start_date: datetime, end_date: datetime = None, count: int = None):
        """
        Create a series of recurring tasks based on a template and schedule.
        This can be used when initially creating a recurring task series.
        """
        instances_created = []

        # For now, just return the original task - in a real system, this would create multiple instances
        # based on the recurrence pattern
        current_date = start_date
        counter = 0

        # This is a simplified version - a full implementation would generate all instances
        # based on the recurrence rule until the end condition is met

        return instances_created