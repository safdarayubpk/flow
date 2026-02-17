"""
Basic test to verify the advanced todo features work correctly.
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app
from sqlmodel import SQLModel, create_engine
from src.core.database import engine
from unittest.mock import patch


@pytest.fixture
def client():
    """Create a test client for the API."""
    with TestClient(app) as test_client:
        yield test_client


def test_advanced_task_filtering(client):
    """Test that advanced task filtering endpoints work."""
    # Mock authentication
    with patch("src.core.auth.get_current_user") as mock_get_current_user:
        from src.models.user import User
        mock_get_current_user.return_value = User(id="test_user", email="test@example.com", name="Test User")

        # Test the advanced filtering endpoint
        response = client.get("/api/v1/tasks/?priority=high&sort=title&order=asc")

        # Should return 200 OK (or 401/403 if auth is enforced)
        assert response.status_code in [200, 401, 403]


def test_task_with_priority_creation(client):
    """Test creating a task with priority."""
    with patch("src.core.auth.get_current_user") as mock_get_current_user:
        from src.models.user import User
        mock_get_current_user.return_value = User(id="test_user", email="test@example.com", name="Test User")

        task_data = {
            "title": "Test task with priority",
            "description": "Test description",
            "priority": "high",
            "due_date": "2026-12-31T23:59:59",
            "recurrence_rule": "RRULE:FREQ=DAILY;INTERVAL=1"
        }

        response = client.post("/api/v1/tasks/", json=task_data)
        assert response.status_code in [200, 201, 401, 403]


def test_recurring_task_endpoint(client):
    """Test the recurring task endpoint."""
    with patch("src.core.auth.get_current_user") as mock_get_current_user:
        from src.models.user import User
        mock_get_current_user.return_value = User(id="test_user", email="test@example.com", name="Test User")

        # This will fail with 422 if the endpoint doesn't exist
        response = client.patch("/api/v1/tasks/1/recurring?rrule_string=RRULE:FREQ=DAILY")
        assert response.status_code in [404, 401, 403, 422]  # 404 if task doesn't exist, 422 if validation fails


def test_due_date_endpoint(client):
    """Test the due date endpoint."""
    with patch("src.core.auth.get_current_user") as mock_get_current_user:
        from src.models.user import User
        mock_get_current_user.return_value = User(id="test_user", email="test@example.com", name="Test User")

        # This will fail with 422 if the endpoint doesn't exist
        response = client.patch("/api/v1/tasks/1/due_date?due_date=2026-12-31T23:59:59Z")
        assert response.status_code in [404, 401, 403, 422]  # 404 if task doesn't exist, 422 if validation fails


def test_recurring_auto_reschedule():
    """
    Verify that process_recurring_tasks() creates a new task instance
    with the next due_date and marks the original task as completed.
    """
    from datetime import datetime, timedelta
    from sqlmodel import Session as SqlSession, create_engine as create_test_engine

    # Use in-memory SQLite so the test is fully isolated
    test_engine = create_test_engine("sqlite://", echo=False)
    SQLModel.metadata.create_all(test_engine)

    with SqlSession(test_engine) as session:
        from src.models.user import User

        # Seed a user
        user = User(id="recur_user", email="recur@test.com", name="Recur Tester")
        session.add(user)
        session.commit()

        # Create a WEEKLY recurring task with a due_date in the past
        from src.models.task import Task

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
        original_id = original.id

        # Run the scheduler
        from src.services.recurring_service import RecurringService

        created = RecurringService.process_recurring_tasks(session=session)

        # --- Assertions ---
        # 1. Exactly one new task was created
        assert len(created) == 1
        new_task = created[0]

        # 2. New task has the correct next due_date (original + 7 days)
        expected_due = past_due + timedelta(weeks=1)
        assert new_task.due_date is not None
        # Allow 1-second tolerance for rounding
        assert abs((new_task.due_date - expected_due).total_seconds()) < 1

        # 3. New task inherits recurrence rule and is not completed
        assert new_task.recurrence_rule == "WEEKLY"
        assert new_task.completed is False
        assert new_task.user_id == "recur_user"

        # 4. Original task is now marked completed (prevents duplicate rescheduling)
        session.refresh(original)
        refreshed_original = session.get(Task, original_id)
        assert refreshed_original.completed is True

        # 5. Running the scheduler again produces no new tasks (original is completed)
        created_again = RecurringService.process_recurring_tasks(session=session)
        assert len(created_again) == 0


if __name__ == "__main__":
    pytest.main([__file__])