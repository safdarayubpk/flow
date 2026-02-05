"""
Scheduled cleanup for soft-deleted tasks per ADR-003.
This implements scheduled cleanup for soft-deleted tasks after retention period.
"""

from sqlmodel import Session, select
from datetime import datetime, timedelta
from src.models.task import Task
from src.core.database import engine


def cleanup_soft_deleted_tasks(retention_days: int = 30) -> int:
    """
    Permanently delete tasks that have been soft deleted for more than the retention period.

    Args:
        retention_days: Number of days to retain soft-deleted tasks before permanent deletion

    Returns:
        Number of tasks permanently deleted
    """
    cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

    with Session(engine) as session:
        # Find tasks that were soft deleted before the cutoff date
        soft_deleted_tasks = session.exec(
            select(Task)
            .where(Task.deleted_at.is_not(None))
            .where(Task.deleted_at < cutoff_date)
        ).all()

        deleted_count = 0
        for task in soft_deleted_tasks:
            session.delete(task)
            deleted_count += 1

        session.commit()
        return deleted_count


def schedule_cleanup_job():
    """
    Schedule the cleanup job to run periodically.
    In a real application, this would be integrated with a scheduler like Celery or APScheduler.
    """
    print("Scheduling cleanup job for soft-deleted tasks...")
    # In a real implementation, you would schedule this with a proper scheduler
    # For example, with APScheduler:
    # scheduler.add_job(cleanup_soft_deleted_tasks, 'interval', days=1)