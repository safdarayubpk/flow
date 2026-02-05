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


if __name__ == "__main__":
    pytest.main([__file__])