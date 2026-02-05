#!/usr/bin/env python3
"""
Simple test to verify CRUD operations work with the updated models
"""
import os
import tempfile
from sqlmodel import SQLModel, create_engine, Session
from src.models.task import Task, TaskCreate, TaskUpdate
from src.models.user import User
from src.services.task_service import TaskService

def test_crud_operations():
    """Test all CRUD operations with the updated models"""

    # Create an in-memory SQLite database for testing
    engine = create_engine("sqlite:///:memory:", echo=True)
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

        print("Testing CREATE operation...")
        # Test creating a task with basic fields
        task_create_data = TaskCreate(
            title="Test Task",
            description="This is a test task",
            priority="high",
            tags=["test", "important"],
            reminder_enabled=True
        )

        created_task = TaskService.create_task(
            session=session,
            task_create=task_create_data,
            user_id=user_id
        )

        assert created_task.title == "Test Task"
        assert created_task.description == "This is a test task"
        assert created_task.priority == "high"
        assert "test" in created_task.tags
        assert "important" in created_task.tags
        assert created_task.reminder_enabled is True
        print("✓ CREATE operation successful")

        print("Testing READ operation...")
        # Test reading the created task
        retrieved_task = TaskService.get_task_by_id(
            session=session,
            task_id=created_task.id,
            user_id=user_id
        )

        assert retrieved_task is not None
        assert retrieved_task.id == created_task.id
        assert retrieved_task.title == "Test Task"
        print("✓ READ operation successful")

        print("Testing UPDATE operation...")
        # Test updating the task
        task_update_data = TaskUpdate(
            title="Updated Test Task",
            priority="low",
            tags=["updated", "test"],
            completed=True
        )

        updated_task = TaskService.update_task(
            session=session,
            task_id=created_task.id,
            task_update=task_update_data,
            user_id=user_id
        )

        assert updated_task is not None
        assert updated_task.title == "Updated Test Task"
        assert updated_task.priority == "low"
        assert "updated" in updated_task.tags
        assert updated_task.completed is True
        print("✓ UPDATE operation successful")

        print("Testing FILTER operation...")
        # Test filtering tasks
        filtered_tasks = TaskService.get_filtered_tasks(
            session=session,
            user_id=user_id,
            priority="low"
        )

        assert len(filtered_tasks) >= 1
        assert any(task.priority == "low" for task in filtered_tasks)
        print("✓ FILTER operation successful")

        print("Testing DELETE operation...")
        # Test deleting the task
        delete_success = TaskService.delete_task(
            session=session,
            task_id=created_task.id,
            user_id=user_id
        )

        assert delete_success is True
        print("✓ DELETE operation successful")

        # Verify task is deleted
        deleted_task = TaskService.get_task_by_id(
            session=session,
            task_id=created_task.id,
            user_id=user_id
        )

        # With soft delete, the task should still exist but have deleted_at set
        # Let's check if it's gone from regular queries
        all_tasks = TaskService.get_active_tasks(session, user_id)
        assert len(all_tasks) == 0
        print("✓ DELETE verification successful")

    print("\n🎉 All CRUD operations verified successfully!")
    return True

if __name__ == "__main__":
    test_crud_operations()