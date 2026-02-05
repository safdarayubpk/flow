from typing import Dict, Any, List
from sqlmodel import Session, select
from src.models.task import Task
from src.models.user import User
from src.services.task_service import TaskService
from src.core.database import get_session


def add_task_tool(user_id: str, title: str, description: str = None) -> Dict[str, Any]:
    """
    MCP tool for adding a new task.
    """
    try:
        # Create a new task for the specified user
        from src.core.database import engine

        with Session(engine) as session:
            # Verify user exists
            user = session.get(User, user_id)
            if not user:
                return {"error": "User not found", "status": "failed"}

            # Create task data
            task_data = {
                "title": title,
                "description": description
            }

            # Create the task
            from src.models.task import TaskCreate
            task_create = TaskCreate(**task_data)
            new_task = TaskService.create_task(session=session, task_create=task_create, user_id=user_id)

            return {
                "task_id": new_task.id,
                "status": "created",
                "title": new_task.title,
                "description": new_task.description
            }
    except Exception as e:
        return {"error": str(e), "status": "failed"}


def list_tasks_tool(user_id: str, status: str = "all") -> List[Dict[str, Any]]:
    """
    MCP tool for listing tasks with optional filtering.
    """
    try:
        from src.core.database import engine

        with Session(engine) as session:
            # Verify user exists
            user = session.get(User, user_id)
            if not user:
                return [{"error": "User not found"}]

            # Get tasks based on status filter
            tasks = TaskService.get_active_tasks(session=session, user_id=user_id)

            # Filter based on status if specified
            if status == "pending":
                tasks = [task for task in tasks if not task.completed]
            elif status == "completed":
                tasks = [task for task in tasks if task.completed]
            # If status is "all", return all tasks (no additional filtering needed)

            # Convert tasks to dict format
            result = []
            for task in tasks:
                result.append({
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat()
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


def update_task_tool(user_id: str, task_id: int, title: str = None, description: str = None) -> Dict[str, Any]:
    """
    MCP tool for updating task details.
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
            update_data = {}
            if title is not None:
                update_data["title"] = title
            if description is not None:
                update_data["description"] = description

            if not update_data:
                return {"error": "No fields to update provided", "status": "failed"}

            # Update the task
            from src.models.task import TaskUpdate
            task_update = TaskUpdate(**update_data)
            updated_task = TaskService.update_task(
                session=session,
                task_id=task_id,
                task_update=task_update,
                user_id=user_id
            )

            return {
                "task_id": updated_task.id,
                "status": "updated",
                "title": updated_task.title
            }
    except Exception as e:
        return {"error": str(e), "status": "failed"}


def filter_tasks_tool(user_id: str, priority: str = None, tags: List[str] = None, due_date_before: str = None) -> List[Dict[str, Any]]:
    """
    MCP tool for filtering tasks by priority, tags, and due date.
    """
    try:
        from src.core.database import engine
        from datetime import datetime

        with Session(engine) as session:
            # Verify user exists
            user = session.get(User, user_id)
            if not user:
                return [{"error": "User not found"}]

            # Parse due date if provided
            parsed_due_date = None
            if due_date_before:
                try:
                    parsed_due_date = datetime.fromisoformat(due_date_before.replace('Z', '+00:00'))
                except ValueError:
                    return [{"error": "Invalid due date format. Use ISO format (YYYY-MM-DDTHH:MM:SSZ)"}]

            # Get filtered tasks
            tasks = TaskService.get_filtered_tasks(
                session=session,
                user_id=user_id,
                priority=priority,
                tags=tags,
                due_date_before=parsed_due_date,
                sort_field=None,
                recurring=None,
                skip=0,
                limit=100
            )

            # Convert tasks to dict format
            result = []
            for task in tasks:
                result.append({
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "priority": task.priority,
                    "tags": task.tags,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "recurrence_rule": task.recurrence_rule,
                    "reminder_enabled": task.reminder_enabled,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat()
                })

            return result
    except Exception as e:
        return [{"error": str(e)}]


def sort_tasks_tool(user_id: str, sort_by: str = "created_at", order: str = "desc") -> List[Dict[str, Any]]:
    """
    MCP tool for sorting tasks by various criteria.
    """
    try:
        from src.core.database import engine

        with Session(engine) as session:
            # Verify user exists
            user = session.get(User, user_id)
            if not user:
                return [{"error": "User not found"}]

            # Validate sort_by parameter
            valid_sort_fields = ["priority", "due_date", "title", "created_at"]
            if sort_by not in valid_sort_fields:
                return [{"error": f"Invalid sort field. Valid options: {valid_sort_fields}"}]

            # Validate order parameter
            if order not in ["asc", "desc"]:
                return [{"error": "Invalid order. Use 'asc' or 'desc'"}]

            # Get sorted tasks
            tasks = TaskService.get_filtered_tasks(
                session=session,
                user_id=user_id,
                sort_field=sort_by,
                order=order,
                skip=0,
                limit=100
            )

            # Convert tasks to dict format
            result = []
            for task in tasks:
                result.append({
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "priority": task.priority,
                    "tags": task.tags,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "recurrence_rule": task.recurrence_rule,
                    "reminder_enabled": task.reminder_enabled,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat()
                })

            return result
    except Exception as e:
        return [{"error": str(e)}]


def set_due_date_tool(user_id: str, task_id: int, due_date: str) -> Dict[str, Any]:
    """
    MCP tool for setting due date on a task.
    """
    try:
        from src.core.database import engine
        from datetime import datetime

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

            # Parse due date
            try:
                parsed_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            except ValueError:
                return {"error": "Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SSZ)", "status": "failed"}

            # Update the task with due date
            from src.models.task import TaskUpdate
            task_update = TaskUpdate(due_date=parsed_date)
            updated_task = TaskService.update_task(
                session=session,
                task_id=task_id,
                task_update=task_update,
                user_id=user_id
            )

            return {
                "task_id": updated_task.id,
                "status": "due date updated",
                "title": updated_task.title,
                "due_date": updated_task.due_date.isoformat() if updated_task.due_date else None
            }
    except Exception as e:
        return {"error": str(e), "status": "failed"}


def set_recurring_tool(user_id: str, task_id: int, rrule_string: str) -> Dict[str, Any]:
    """
    MCP tool for setting recurring pattern on a task.
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

            # Validate rrule_string format (basic validation)
            if not rrule_string or not isinstance(rrule_string, str) or len(rrule_string) < 5:
                return {"error": "Invalid rrule string format", "status": "failed"}

            # Update the task with recurrence rule
            from src.models.task import TaskUpdate
            task_update = TaskUpdate(recurrence_rule=rrule_string)
            updated_task = TaskService.update_task(
                session=session,
                task_id=task_id,
                task_update=task_update,
                user_id=user_id
            )

            return {
                "task_id": updated_task.id,
                "status": "recurring pattern updated",
                "title": updated_task.title,
                "recurrence_rule": updated_task.recurrence_rule
            }
    except Exception as e:
        return {"error": str(e), "status": "failed"}