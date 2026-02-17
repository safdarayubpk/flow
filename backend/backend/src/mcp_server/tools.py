from typing import Dict, Any, List, Optional
from sqlmodel import Session, select
from src.models.task import Task
from src.models.user import User
from src.services.task_service import TaskService
from src.core.database import get_session


def add_task_tool(
    user_id: str,
    title: str,
    description: str = None,
    priority: str = None,
    tags: List[str] = None,
    due_date: str = None,
    recurrence_rule: str = None,
    reminder_enabled: bool = False,
) -> Dict[str, Any]:
    """
    MCP tool for adding a new task with optional Phase V.1 fields.
    """
    try:
        from src.core.database import engine

        with Session(engine) as session:
            # Verify user exists
            user = session.get(User, user_id)
            if not user:
                return {"error": "User not found", "status": "failed"}

            # Build task data with Phase V.1 fields
            task_data: Dict[str, Any] = {
                "title": title,
                "description": description,
            }
            if priority is not None:
                task_data["priority"] = priority
            if due_date is not None:
                from datetime import datetime as dt
                task_data["due_date"] = dt.fromisoformat(due_date.replace("Z", "+00:00"))
            if recurrence_rule is not None:
                task_data["recurrence_rule"] = recurrence_rule
            if reminder_enabled:
                task_data["reminder_enabled"] = True

            # Create the task
            from src.models.task import TaskCreate
            task_create = TaskCreate(**task_data)
            new_task = TaskService.create_task(session=session, task_create=task_create, user_id=user_id)

            # Link tags if provided
            if tags:
                TaskService.resolve_and_link_tags(
                    session=session, task_id=new_task.id, user_id=user_id, tag_names=tags
                )

            # Build response with all Phase V.1 fields
            tag_names = tags or []
            return {
                "task_id": new_task.id,
                "status": "created",
                "title": new_task.title,
                "description": new_task.description,
                "priority": new_task.priority,
                "tags": tag_names,
                "due_date": new_task.due_date.isoformat() if new_task.due_date else None,
                "recurrence_rule": new_task.recurrence_rule,
                "reminder_enabled": new_task.reminder_enabled,
            }
    except Exception as e:
        return {"error": str(e), "status": "failed"}


def list_tasks_tool(
    user_id: str,
    status: str = "all",
    priority: str = None,
    tags: List[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> List[Dict[str, Any]]:
    """
    MCP tool for listing tasks with optional filtering, tag filtering, and sorting.
    """
    try:
        from src.core.database import engine

        with Session(engine) as session:
            # Verify user exists
            user = session.get(User, user_id)
            if not user:
                return [{"error": "User not found"}]

            # Use get_filtered_tasks for priority/sort support
            tasks = TaskService.get_filtered_tasks(
                session=session,
                user_id=user_id,
                priority=priority,
                sort_field=sort_by,
                order=sort_order,
            )

            # Filter based on completion status
            if status == "pending":
                tasks = [task for task in tasks if not task.completed]
            elif status == "completed":
                tasks = [task for task in tasks if task.completed]

            # Batch-load tags for all tasks
            task_ids = [task.id for task in tasks]
            tag_map = TaskService.get_tasks_tag_names_batch(session=session, task_ids=task_ids)

            # Filter by tags if requested
            if tags:
                tags_lower = {t.lower() for t in tags}
                tasks = [
                    task for task in tasks
                    if tags_lower & {t.lower() for t in tag_map.get(task.id, [])}
                ]

            # Convert tasks to dict format with Phase V.1 fields
            result = []
            for task in tasks:
                result.append({
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "priority": task.priority,
                    "tags": tag_map.get(task.id, []),
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "recurrence_rule": task.recurrence_rule,
                    "reminder_enabled": task.reminder_enabled,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat(),
                })

            return result
    except Exception as e:
        return [{"error": str(e)}]


def complete_task_tool(user_id: str, task_id: int) -> Dict[str, Any]:
    """
    MCP tool for marking a task as complete.
    """
    try:
        from src.core.database import engine

        with Session(engine) as session:
            # Verify user exists
            user = session.get(User, user_id)
            if not user:
                return {"error": "User not found", "status": "failed"}

            # Verify task exists and belongs to user
            statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
            task = session.exec(statement).first()

            if not task:
                return {"error": "Task not found or does not belong to user", "status": "failed"}

            # Toggle completion status
            task.completed = not task.completed
            session.add(task)
            session.commit()
            session.refresh(task)

            return {
                "task_id": task.id,
                "status": "completed" if task.completed else "marked pending",
                "title": task.title
            }
    except Exception as e:
        return {"error": str(e), "status": "failed"}


def delete_task_tool(user_id: str, task_id: int) -> Dict[str, Any]:
    """
    MCP tool for deleting a task.
    """
    try:
        from src.core.database import engine

        with Session(engine) as session:
            # Verify user exists
            user = session.get(User, user_id)
            if not user:
                return {"error": "User not found", "status": "failed"}

            # Verify task exists and belongs to user
            statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
            task = session.exec(statement).first()

            if not task:
                return {"error": "Task not found or does not belong to user", "status": "failed"}

            # Perform soft delete using TaskService
            success = TaskService.delete_task(session=session, task_id=task_id, user_id=user_id)

            if success:
                return {
                    "task_id": task_id,
                    "status": "deleted",
                    "title": task.title
                }
            else:
                return {"error": "Failed to delete task", "status": "failed"}
    except Exception as e:
        return {"error": str(e), "status": "failed"}


def update_task_tool(
    user_id: str,
    task_id: int,
    title: str = None,
    description: str = None,
    priority: str = None,
    tags: List[str] = None,
    due_date: str = None,
    recurrence_rule: str = None,
    reminder_enabled: bool = None,
) -> Dict[str, Any]:
    """
    MCP tool for updating task details including Phase V.1 fields.
    """
    try:
        from src.core.database import engine

        with Session(engine) as session:
            # Verify user exists
            user = session.get(User, user_id)
            if not user:
                return {"error": "User not found", "status": "failed"}

            # Verify task exists and belongs to user
            statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
            task = session.exec(statement).first()

            if not task:
                return {"error": "Task not found or does not belong to user", "status": "failed"}

            # Prepare update data
            update_data: Dict[str, Any] = {}
            if title is not None:
                update_data["title"] = title
            if description is not None:
                update_data["description"] = description
            if priority is not None:
                update_data["priority"] = priority
            if due_date is not None:
                from datetime import datetime as dt
                update_data["due_date"] = dt.fromisoformat(due_date.replace("Z", "+00:00"))
            if recurrence_rule is not None:
                update_data["recurrence_rule"] = recurrence_rule
            if reminder_enabled is not None:
                update_data["reminder_enabled"] = reminder_enabled

            # Tags are handled separately but we still need at least one field or tags
            if not update_data and tags is None:
                return {"error": "No fields to update provided", "status": "failed"}

            # Update scalar fields if any
            if update_data:
                from src.models.task import TaskUpdate
                task_update = TaskUpdate(**update_data)
                task = TaskService.update_task(
                    session=session,
                    task_id=task_id,
                    task_update=task_update,
                    user_id=user_id,
                )

            # Link tags if provided
            if tags is not None:
                TaskService.resolve_and_link_tags(
                    session=session, task_id=task_id, user_id=user_id, tag_names=tags
                )

            # Fetch current tag names for response
            tag_names = TaskService.get_task_tag_names(session=session, task_id=task_id)

            return {
                "task_id": task.id,
                "status": "updated",
                "title": task.title,
                "description": task.description,
                "priority": task.priority,
                "tags": tag_names,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "recurrence_rule": task.recurrence_rule,
                "reminder_enabled": task.reminder_enabled,
            }
    except Exception as e:
        return {"error": str(e), "status": "failed"}