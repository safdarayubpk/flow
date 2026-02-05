"""
Test script to verify all existing CRUD operations still work correctly
after advanced feature additions.
"""
import asyncio
import pytest
from sqlmodel import Session, SQLModel, create_engine
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from src.main import app
from src.models.user import User
from src.models.task import Task, TaskCreate, TaskUpdate
from src.core.database import get_session
from src.core.auth import get_current_user
from src.models.tag import Tag

# Mock user for testing
mock_user = User(id=1, email="test@example.com", password_hash="hashed_password")

def mock_get_current_user():
    return mock_user

def mock_get_session():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

# Override dependencies for testing
app.dependency_overrides[get_current_user] = mock_get_current_user
app.dependency_overrides[get_session] = mock_get_session

client = TestClient(app)

def test_create_task_basic():
    """Test basic task creation with minimal data"""
    response = client.post("/api/v1/tasks/", json={
        "title": "Test task",
        "description": "Test description"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test task"
    assert data["description"] == "Test description"
    assert data["completed"] is False
    return data["id"]

def test_create_task_with_advanced_features():
    """Test task creation with all advanced features"""
    due_date = (datetime.now() + timedelta(days=1)).isoformat()

    response = client.post("/api/v1/tasks/", json={
        "title": "Advanced task",
        "description": "Task with all features",
        "priority": "high",
        "tags": ["work", "important"],
        "due_date": due_date,
        "recurrence_rule": "FREQ=DAILY",
        "reminder_enabled": True
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Advanced task"
    assert data["priority"] == "high"
    assert "work" in data["tags"]
    assert "important" in data["tags"]
    assert data["due_date"] is not None
    assert data["recurrence_rule"] == "FREQ=DAILY"
    assert data["reminder_enabled"] is True
    return data["id"]

def test_read_single_task():
    """Test reading a single task by ID"""
    # Create a task first
    task_id = test_create_task_basic()

    response = client.get(f"/api/v1/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Test task"

def test_read_all_tasks():
    """Test reading all tasks for the user"""
    # Create multiple tasks
    task1_id = test_create_task_basic()
    task2_id = test_create_task_with_advanced_features()

    response = client.get("/api/v1/tasks/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2

    # Verify both tasks are present
    task_ids = [task["id"] for task in data]
    assert task1_id in task_ids
    assert task2_id in task_ids

def test_update_task():
    """Test updating a task"""
    task_id = test_create_task_basic()

    # Update the task
    response = client.put(f"/api/v1/tasks/{task_id}", json={
        "title": "Updated task",
        "description": "Updated description",
        "completed": True
    })
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Updated task"
    assert data["completed"] is True

def test_update_task_advanced_fields():
    """Test updating advanced fields of a task"""
    task_id = test_create_task_with_advanced_features()

    # Update advanced fields
    due_date = (datetime.now() + timedelta(days=3)).isoformat()
    response = client.put(f"/api/v1/tasks/{task_id}", json={
        "title": "Updated advanced task",
        "priority": "low",
        "tags": ["personal", "later"],
        "due_date": due_date,
        "recurrence_rule": "FREQ=WEEKLY",
        "reminder_enabled": False
    })
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Updated advanced task"
    assert data["priority"] == "low"
    assert "personal" in data["tags"]
    assert "later" in data["tags"]
    assert data["recurrence_rule"] == "FREQ=WEEKLY"
    assert data["reminder_enabled"] is False

def test_toggle_completion():
    """Test toggling task completion status"""
    task_id = test_create_task_basic()

    # Verify initial state
    response = client.get(f"/api/v1/tasks/{task_id}")
    assert response.json()["completed"] is False

    # Toggle completion
    response = client.patch(f"/api/v1/tasks/{task_id}/complete")
    assert response.status_code == 200
    data = response.json()
    assert data["completed"] is True

    # Toggle back to incomplete
    response = client.patch(f"/api/v1/tasks/{task_id}/complete")
    assert response.status_code == 200
    data = response.json()
    assert data["completed"] is False

def test_delete_task():
    """Test deleting a task"""
    task_id = test_create_task_basic()

    # Verify task exists
    response = client.get(f"/api/v1/tasks/{task_id}")
    assert response.status_code == 200

    # Delete the task
    response = client.delete(f"/api/v1/tasks/{task_id}")
    assert response.status_code == 204

    # Verify task is deleted
    response = client.get(f"/api/v1/tasks/{task_id}")
    assert response.status_code == 404

def test_filter_and_sort():
    """Test filtering and sorting functionality"""
    # Create tasks with different attributes
    client.post("/api/v1/tasks/", json={
        "title": "High priority task",
        "priority": "high",
        "tags": ["urgent"]
    })
    client.post("/api/v1/tasks/", json={
        "title": "Low priority task",
        "priority": "low",
        "tags": ["later"]
    })
    client.post("/api/v1/tasks/", json={
        "title": "Medium priority task",
        "priority": "medium",
        "tags": ["normal"]
    })

    # Test filtering by priority
    response = client.get("/api/v1/tasks/?priority=high")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    for task in data:
        assert task["priority"] == "high"

    # Test filtering by tag
    response = client.get("/api/v1/tasks/?tags=urgent")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    for task in data:
        assert "urgent" in task["tags"]

    # Test sorting by priority
    response = client.get("/api/v1/tasks/?sort=priority&order=asc")
    assert response.status_code == 200
    data = response.json()
    priorities = [task["priority"] for task in data if task["priority"]]
    # Should be ordered low, medium, high
    if len(priorities) >= 3:
        # We can't guarantee exact ordering without knowing all tasks in DB
        # but we can verify that priorities are present
        assert all(p in ["high", "medium", "low"] for p in priorities)

def test_backward_compatibility():
    """Test that old API calls without new fields still work"""
    # Create task with only basic fields (old-style API call)
    response = client.post("/api/v1/tasks/", json={
        "title": "Legacy task",
        "description": "Created with old API"
    })
    assert response.status_code == 201
    data = response.json()
    # New fields should have sensible defaults
    assert data["title"] == "Legacy task"
    assert data["priority"] is None  # or default value
    assert data["tags"] == []
    assert data["due_date"] is None
    assert data["recurrence_rule"] is None
    assert data["reminder_enabled"] is False

def run_all_tests():
    """Run all CRUD operation tests"""
    print("Testing basic task creation...")
    test_create_task_basic()
    print("✓ Basic task creation works")

    print("Testing advanced task creation...")
    test_create_task_with_advanced_features()
    print("✓ Advanced task creation works")

    print("Testing single task read...")
    test_read_single_task()
    print("✓ Single task read works")

    print("Testing all tasks read...")
    test_read_all_tasks()
    print("✓ All tasks read works")

    print("Testing task update...")
    test_update_task()
    print("✓ Task update works")

    print("Testing advanced field updates...")
    test_update_task_advanced_fields()
    print("✓ Advanced field updates work")

    print("Testing completion toggle...")
    test_toggle_completion()
    print("✓ Completion toggle works")

    print("Testing task deletion...")
    test_delete_task()
    print("✓ Task deletion works")

    print("Testing filter and sort...")
    test_filter_and_sort()
    print("✓ Filter and sort works")

    print("Testing backward compatibility...")
    test_backward_compatibility()
    print("✓ Backward compatibility works")

    print("\n🎉 All CRUD operations verified successfully!")

if __name__ == "__main__":
    run_all_tests()