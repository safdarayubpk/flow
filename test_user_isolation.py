#!/usr/bin/env python3
"""
Test to verify user isolation is maintained across all new features
"""
import os
import tempfile
from sqlmodel import SQLModel, create_engine, Session
from src.models.task import Task, TaskCreate, TaskUpdate
from src.models.user import User
from src.services.task_service import TaskService

def test_user_isolation():
    """Test that users can only access their own tasks"""

    # Create an in-memory SQLite database for testing
    engine = create_engine("sqlite:///:memory:", echo=False)
    SQLModel.metadata.create_all(engine)

    # Create two test users
    user1 = User(
        id="user_123",
        email="user1@example.com",
        password_hash="hashed_password"
    )

    user2 = User(
        id="user_456",
        email="user2@example.com",
        password_hash="hashed_password"
    )

    with Session(engine) as session:
        session.add(user1)
        session.add(user2)
        session.commit()

        print("Testing user isolation...")

        # User 1 creates a task
        task_create_data = TaskCreate(
            title="User 1 Task",
            description="This belongs to user 1",
            priority="high",
            tags=["user1", "important"],
            reminder_enabled=True
        )

        user1_task = TaskService.create_task(
            session=session,
            task_create=task_create_data,
            user_id=user1.id
        )

        # User 2 creates a task
        task_create_data2 = TaskCreate(
            title="User 2 Task",
            description="This belongs to user 2",
            priority="low",
            tags=["user2", "normal"],
            reminder_enabled=False
        )

        user2_task = TaskService.create_task(
            session=session,
            task_create=task_create_data2,
            user_id=user2.id
        )

        # Verify each user can only see their own tasks
        user1_tasks = TaskService.get_active_tasks(session, user1.id)
        user2_tasks = TaskService.get_active_tasks(session, user2.id)

        assert len(user1_tasks) == 1
        assert user1_tasks[0].title == "User 1 Task"
        assert user1_tasks[0].id == user1_task.id
        print("✓ User 1 can only see their own tasks")

        assert len(user2_tasks) == 1
        assert user2_tasks[0].title == "User 2 Task"
        assert user2_tasks[0].id == user2_task.id
        print("✓ User 2 can only see their own tasks")

        # Test that users cannot access each other's tasks
        user1_task_access = TaskService.get_task_by_id(
            session=session,
            task_id=user2_task.id,  # Trying to access user2's task
            user_id=user1.id         # But logged in as user1
        )

        assert user1_task_access is None
        print("✓ User 1 cannot access User 2's tasks")

        user2_task_access = TaskService.get_task_by_id(
            session=session,
            task_id=user1_task.id,  # Trying to access user1's task
            user_id=user2.id         # But logged in as user2
        )

        assert user2_task_access is None
        print("✓ User 2 cannot access User 1's tasks")

        # Test filtering - each user should only get their own filtered results
        user1_filtered = TaskService.get_filtered_tasks(
            session=session,
            user_id=user1.id,
            priority="high"
        )

        assert len(user1_filtered) == 1
        assert user1_filtered[0].id == user1_task.id
        print("✓ User 1 filtering only returns their tasks")

        user2_filtered = TaskService.get_filtered_tasks(
            session=session,
            user_id=user2.id,
            priority="low"
        )

        assert len(user2_filtered) == 1
        assert user2_filtered[0].id == user2_task.id
        print("✓ User 2 filtering only returns their tasks")

        # Test update isolation - user1 should not be able to update user2's task
        update_result = TaskService.update_task(
            session=session,
            task_id=user2_task.id,  # Trying to update user2's task
            task_update=TaskUpdate(title="Hacked task"),
            user_id=user1.id         # But logged in as user1
        )

        assert update_result is None
        print("✓ User 1 cannot update User 2's tasks")

        # Test delete isolation - user1 should not be able to delete user2's task
        delete_result = TaskService.delete_task(
            session=session,
            task_id=user2_task.id,  # Trying to delete user2's task
            user_id=user1.id         # But logged in as user1
        )

        assert delete_result is False
        print("✓ User 1 cannot delete User 2's tasks")

    print("\n🎉 User isolation verified successfully!")
    return True

if __name__ == "__main__":
    test_user_isolation()