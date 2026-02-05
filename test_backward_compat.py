#!/usr/bin/env python3
"""
Test to verify backward compatibility with old API calls
"""
import os
import tempfile
from sqlmodel import SQLModel, create_engine, Session
from src.models.task import Task, TaskCreate, TaskUpdate
from src.models.user import User
from src.services.task_service import TaskService

def test_backward_compatibility():
    """Test that old API calls without new fields still work"""

    # Create an in-memory SQLite database for testing
    engine = create_engine("sqlite:///:memory:", echo=False)
    SQLModel.metadata.create_all(engine)

    # Create a test user
    test_user = User(
        id="test_user_123",
        email="test@example.com",
        password_hash="hashed_password"
    )

    with Session(engine) as session:
        session.add(test_user)
        session.commit()

        user_id = test_user.id

        print("Testing backward compatibility...")

        # Test creating a task with only basic fields (old-style API call)
        basic_task_data = TaskCreate(
            title="Basic Task",
            description="Task created with old API"
        )

        basic_task = TaskService.create_task(
            session=session,
            task_create=basic_task_data,
            user_id=user_id
        )

        # Verify the task was created and new fields have appropriate defaults
        assert basic_task.title == "Basic Task"
        assert basic_task.description == "Task created with old API"
        assert basic_task.priority is None  # Should default to None
        assert basic_task.tags == []  # Should default to empty list
        assert basic_task.due_date is None  # Should default to None
        assert basic_task.recurrence_rule is None  # Should default to None
        assert basic_task.reminder_enabled is False  # Should default to False
        print("✓ Old API calls without new fields work correctly")

        # Test updating a task with only basic fields
        update_basic_data = TaskUpdate(
            title="Updated Basic Task",
            completed=True
        )

        updated_task = TaskService.update_task(
            session=session,
            task_id=basic_task.id,
            task_update=update_basic_data,
            user_id=user_id
        )

        assert updated_task.title == "Updated Basic Task"
        assert updated_task.completed is True
        # Other fields should remain unchanged
        assert updated_task.priority is None
        assert updated_task.tags == []
        print("✓ Updating with basic fields only works correctly")

        # Create a task with new fields to test partial updates
        full_task_data = TaskCreate(
            title="Full Task",
            description="Task with all features",
            priority="high",
            tags=["important", "work"],
            reminder_enabled=True
        )

        full_task = TaskService.create_task(
            session=session,
            task_create=full_task_data,
            user_id=user_id
        )

        # Update only basic fields - advanced fields should remain unchanged
        partial_update = TaskUpdate(
            title="Partially Updated Full Task"
        )

        partially_updated = TaskService.update_task(
            session=session,
            task_id=full_task.id,
            task_update=partial_update,
            user_id=user_id
        )

        assert partially_updated.title == "Partially Updated Full Task"
        # Advanced fields should remain unchanged
        assert partially_updated.priority == "high"
        assert "important" in partially_updated.tags
        assert "work" in partially_updated.tags
        assert partially_updated.reminder_enabled is True
        print("✓ Partial updates preserve advanced fields")

        # Test that filtering still works for tasks without advanced features
        basic_tasks = TaskService.get_filtered_tasks(
            session=session,
            user_id=user_id,
            priority=None  # Should still work even though we have advanced filtering
        )

        assert len(basic_tasks) >= 2  # Should include both tasks we created
        print("✓ Filtering works with mixed old/new tasks")

        # Test that old behavior is preserved - completed field should still work
        all_tasks = TaskService.get_active_tasks(session, user_id)
        assert len(all_tasks) >= 2
        print("✓ Legacy get_active_tasks still works")

    print("\n🎉 Backward compatibility verified successfully!")
    return True

if __name__ == "__main__":
    test_backward_compatibility()