#!/usr/bin/env python3
"""
Integration test to verify API endpoints work with advanced features
"""
import json
from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine
from src.main import app
from src.models.user import User
from src.models.task import Task
from src.core.database import get_session
from src.core.auth import get_current_user

# Mock user for testing
mock_user = User(id="test_user_123", email="test@example.com", password_hash="hashed")

def mock_get_current_user():
    return mock_user

def create_test_engine():
    return create_engine("sqlite:///:memory:")

def mock_get_session():
    engine = create_test_engine()
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

# Override dependencies for testing
from sqlmodel import Session
app.dependency_overrides[get_current_user] = mock_get_current_user

def test_api_integration():
    """Test API endpoints with advanced features"""

    # Create a test client
    client = TestClient(app)

    print("Testing API endpoints integration...")

    # Test creating a task with advanced features
    due_date_iso = (datetime.now().replace(hour=9, minute=0, second=0, microsecond=0) +
                   datetime.timedelta(days=1)).isoformat()

    response = client.post("/api/v1/tasks/", json={
        "title": "API Test Task",
        "description": "Task created via API with advanced features",
        "priority": "high",
        "tags": ["api", "test", "important"],
        "due_date": due_date_iso,
        "recurrence_rule": "FREQ=DAILY",
        "reminder_enabled": True
    })

    assert response.status_code == 201
    task_data = response.json()
    assert task_data["title"] == "API Test Task"
    assert task_data["priority"] == "high"
    assert "api" in task_data["tags"]
    assert "test" in task_data["tags"]
    assert "important" in task_data["tags"]
    assert task_data["due_date"] is not None
    assert task_data["recurrence_rule"] == "FREQ=DAILY"
    assert task_data["reminder_enabled"] is True
    print("✓ API task creation with advanced features works")

    task_id = task_data["id"]

    # Test getting the task
    response = client.get(f"/api/v1/tasks/{task_id}")
    assert response.status_code == 200
    retrieved_task = response.json()
    assert retrieved_task["id"] == task_id
    print("✓ API task retrieval works")

    # Test filtering by priority
    response = client.get("/api/v1/tasks/?priority=high")
    assert response.status_code == 200
    filtered_tasks = response.json()
    high_priority_count = len([t for t in filtered_tasks if t["priority"] == "high"])
    assert high_priority_count >= 1
    print("✓ API filtering by priority works")

    # Test filtering by tags
    response = client.get("/api/v1/tasks/?tags=test")
    assert response.status_code == 200
    filtered_tasks = response.json()
    assert len(filtered_tasks) >= 1
    print("✓ API filtering by tags works")

    # Test updating the task
    response = client.put(f"/api/v1/tasks/{task_id}", json={
        "title": "Updated API Test Task",
        "priority": "medium",
        "tags": ["updated", "api", "test"]
    })

    assert response.status_code == 200
    updated_task = response.json()
    assert updated_task["title"] == "Updated API Test Task"
    assert updated_task["priority"] == "medium"
    print("✓ API task update works")

    # Test toggling completion
    response = client.patch(f"/api/v1/tasks/{task_id}/complete")
    assert response.status_code == 200
    toggled_task = response.json()
    assert toggled_task["completed"] is True
    print("✓ API completion toggle works")

    # Test updating due date via specific endpoint
    new_due_date = (datetime.now().replace(hour=10, minute=30) +
                    datetime.timedelta(days=2)).isoformat()

    response = client.patch(f"/api/v1/tasks/{task_id}/due_date?due_date={new_due_date}")
    assert response.status_code == 200
    updated_due_date_task = response.json()
    assert updated_due_date_task["due_date"] is not None
    print("✓ API due date update works")

    # Test updating recurrence via specific endpoint
    response = client.patch(f"/api/v1/tasks/{task_id}/recurring?rrule_string=FREQ=WEEKLY")
    assert response.status_code == 200
    updated_recurrence_task = response.json()
    assert updated_recurrence_task["recurrence_rule"] == "FREQ=WEEKLY"
    print("✓ API recurrence update works")

    print("\n🎉 API integration verified successfully!")
    return True

if __name__ == "__main__":
    test_api_integration()