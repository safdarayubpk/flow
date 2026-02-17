"""
Tests for RecurringService auto-rescheduling.

Runs against an in-memory SQLite database — no .env or external DB required.
"""
import pytest
from datetime import datetime, timedelta
from sqlmodel import SQLModel, Session, create_engine

from src.models.task import Task
from src.models.user import User
from src.services.recurring_service import RecurringService


@pytest.fixture
def session():
    """Provide an in-memory SQLite session with schema + seed user."""
    engine = create_engine("sqlite://", echo=False)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        user = User(id="recur_user", email="recur@test.com", password_hash="fakehash")
        s.add(user)
        s.commit()
        yield s


def test_weekly_recurring_creates_next_instance(session):
    """A WEEKLY task with a past due_date should produce one new task."""
    past_due = datetime.utcnow() - timedelta(days=2)
    original = Task(
        title="Weekly standup",
        user_id="recur_user",
        recurrence_rule="WEEKLY",
        due_date=past_due,
        completed=False,
    )
    session.add(original)
    session.commit()
    session.refresh(original)

    created = RecurringService.process_recurring_tasks(session=session)

    assert len(created) == 1
    new_task = created[0]

    # Next due_date should be original + 7 days
    expected_due = past_due + timedelta(weeks=1)
    assert new_task.due_date is not None
    assert abs((new_task.due_date - expected_due).total_seconds()) < 1

    # Inherits recurrence and belongs to the same user
    assert new_task.recurrence_rule == "WEEKLY"
    assert new_task.completed is False
    assert new_task.user_id == "recur_user"


def test_original_marked_completed_after_reschedule(session):
    """After rescheduling, the original task must be marked completed."""
    past_due = datetime.utcnow() - timedelta(days=1)
    original = Task(
        title="Daily sync",
        user_id="recur_user",
        recurrence_rule="DAILY",
        due_date=past_due,
        completed=False,
    )
    session.add(original)
    session.commit()
    session.refresh(original)
    original_id = original.id

    RecurringService.process_recurring_tasks(session=session)

    session.refresh(original)
    refreshed = session.get(Task, original_id)
    assert refreshed.completed is True


def test_no_duplicate_on_second_run(session):
    """Running the scheduler twice should not create duplicates."""
    past_due = datetime.utcnow() - timedelta(days=3)
    original = Task(
        title="Monthly review",
        user_id="recur_user",
        recurrence_rule="MONTHLY",
        due_date=past_due,
        completed=False,
    )
    session.add(original)
    session.commit()

    first_run = RecurringService.process_recurring_tasks(session=session)
    assert len(first_run) == 1

    # Second run: original is completed, new task's due_date is in the future
    second_run = RecurringService.process_recurring_tasks(session=session)
    assert len(second_run) == 0


def test_future_due_date_not_rescheduled(session):
    """A recurring task whose due_date is still in the future should not be rescheduled."""
    future_due = datetime.utcnow() + timedelta(days=5)
    task = Task(
        title="Future weekly",
        user_id="recur_user",
        recurrence_rule="WEEKLY",
        due_date=future_due,
        completed=False,
    )
    session.add(task)
    session.commit()

    created = RecurringService.process_recurring_tasks(session=session)
    assert len(created) == 0


def test_no_due_date_not_rescheduled(session):
    """A recurring task with no due_date should not be rescheduled."""
    task = Task(
        title="No date weekly",
        user_id="recur_user",
        recurrence_rule="WEEKLY",
        due_date=None,
        completed=False,
    )
    session.add(task)
    session.commit()

    created = RecurringService.process_recurring_tasks(session=session)
    assert len(created) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
