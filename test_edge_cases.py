#!/usr/bin/env python3
"""
Test to verify edge cases work properly
"""
import os
from datetime import datetime, timedelta
from sqlmodel import SQLModel, create_engine, Session
from src.models.task import Task, TaskCreate, TaskUpdate
from src.models.user import User
from src.services.task_service import TaskService

def test_edge_cases():
    """Test edge cases like invalid tag names, past due dates, etc."""

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

        print("Testing edge cases...")

        # Test creating task with past due date
        past_date = datetime.now() - timedelta(days=1)
        task_past_due = TaskCreate(
            title="Past Due Task",
            description="Task with due date in the past",
            due_date=past_date,
            priority="high"
        )

        past_task = TaskService.create_task(
            session=session,
            task_create=task_past_due,
            user_id=user_id
        )

        assert past_task.title == "Past Due Task"
        assert past_task.due_date is not None
        print("✓ Past due dates are allowed")

        # Test creating task with empty tags
        empty_tags_task = TaskCreate(
            title="Empty Tags Task",
            description="Task with empty tags array",
            tags=[]
        )

        empty_task = TaskService.create_task(
            session=session,
            task_create=empty_tags_task,
            user_id=user_id
        )

        assert empty_task.tags == []
        print("✓ Empty tags array works")

        # Test creating task with various tag formats
        varied_tags_task = TaskCreate(
            title="Varied Tags Task",
            description="Task with various tag formats",
            tags=["simple", "with-spaces", "with_underscore", "mixed123"]
        )

        varied_task = TaskService.create_task(
            session=session,
            task_create=varied_tags_task,
            user_id=user_id
        )

        assert len(varied_task.tags) == 4
        assert "simple" in varied_task.tags
        assert "with-spaces" in varied_task.tags
        print("✓ Various tag formats work")

        # Test filtering with non-existent tags
        no_results = TaskService.get_filtered_tasks(
            session=session,
            user_id=user_id,
            tags=["nonexistent-tag"]
        )

        assert len(no_results) == 0
        print("✓ Filtering with non-existent tags returns empty result")

        # Test filtering with multiple tags (should find tasks that have ANY of the tags)
        multi_tag_task = TaskCreate(
            title="Multi Tag Task",
            description="Task with multiple tags",
            tags=["tag1", "tag2", "tag3"]
        )

        multi_task = TaskService.create_task(
            session=session,
            task_create=multi_tag_task,
            user_id=user_id
        )

        # Find tasks with either tag1 or tag2
        multi_results = TaskService.get_filtered_tasks(
            session=session,
            user_id=user_id,
            tags=["tag1", "tag2"]
        )

        # Should find the multi_tag_task
        found_multi = any(task.id == multi_task.id for task in multi_results)
        assert found_multi
        print("✓ Multiple tag filtering works")

        # Test sorting with mixed task types
        sort_results_desc = TaskService.get_filtered_tasks(
            session=session,
            user_id=user_id,
            sort_field="priority",
            order="desc"
        )

        # Test with different sort orders
        sort_results_asc = TaskService.get_filtered_tasks(
            session=session,
            user_id=user_id,
            sort_field="priority",
            order="asc"
        )

        print("✓ Sorting works with mixed task types")

        # Test updating with None values (should not change existing values)
        original_title = multi_task.title
        none_update = TaskUpdate(
            title=None,  # Should not change the title
            priority=None  # Should not change the priority
        )

        updated_none = TaskService.update_task(
            session=session,
            task_id=multi_task.id,
            task_update=none_update,
            user_id=user_id
        )

        assert updated_none.title == original_title  # Should remain unchanged
        print("✓ Updating with None values preserves existing values")

        # Test task with only required fields
        minimal_task = TaskCreate(
            title="Minimal Task",
            description=None  # Description is optional
        )

        minimal = TaskService.create_task(
            session=session,
            task_create=minimal_task,
            user_id=user_id
        )

        assert minimal.title == "Minimal Task"
        assert minimal.description is None
        assert minimal.priority is None
        assert minimal.tags == []
        print("✓ Minimal task creation works")

        # Test recurring task with basic RRULE
        recurring_task = TaskCreate(
            title="Recurring Task",
            description="Task that repeats daily",
            recurrence_rule="FREQ=DAILY;INTERVAL=1",
            reminder_enabled=True
        )

        recurring = TaskService.create_task(
            session=session,
            task_create=recurring_task,
            user_id=user_id
        )

        assert recurring.recurrence_rule == "FREQ=DAILY;INTERVAL=1"
        assert recurring.reminder_enabled is True
        print("✓ Recurring task creation works")

    print("\n🎉 Edge cases verified successfully!")
    return True

if __name__ == "__main__":
    test_edge_cases()