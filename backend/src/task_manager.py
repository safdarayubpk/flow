"""
Task Manager for the Console Todo App.

This module manages the in-memory storage and operations for tasks,
including creating, reading, updating, deleting, and listing tasks.
"""

from typing import Dict, List, Optional
from datetime import datetime
from task_model import Task


class TaskManager:
    """
    Manages the collection of tasks in memory.

    Handles all CRUD operations for tasks using an in-memory dictionary
    that maps task IDs to Task objects.
    """

    def __init__(self):
        """Initialize the task manager with empty storage and ID counter."""
        self._tasks: Dict[int, Task] = {}
        self._next_id: int = 1

    def _validate_task_exists(self, task_id: int) -> None:
        """Validate that a task with the given ID exists."""
        if task_id not in self._tasks:
            raise ValueError(f"Task with ID {task_id} does not exist")

    def _validate_title(self, title: Optional[str]) -> None:
        """Validate that a title is non-empty if provided."""
        if title is not None and (not title or not title.strip()):
            raise ValueError("Task title must be non-empty")

    def create_task(self, title: str, description: Optional[str] = None) -> Task:
        """
        Create a new task with the given title and optional description.

        Args:
            title (str): The task title (required)
            description (str, optional): The task description

        Returns:
            Task: The newly created task object

        Raises:
            ValueError: If title is empty or invalid
        """
        self._validate_title(title)

        task_id = self._next_id
        self._next_id += 1

        task = Task(
            id=task_id,
            title=title.strip(),
            description=description,
            created_at=datetime.now()
        )

        self._tasks[task_id] = task
        return task

    def get_task(self, task_id: int) -> Task:
        """
        Retrieve a task by its ID.

        Args:
            task_id (int): The ID of the task to retrieve

        Returns:
            Task: The task object with the given ID

        Raises:
            ValueError: If task with the given ID does not exist
        """
        self._validate_task_exists(task_id)
        return self._tasks[task_id]

    def list_tasks(self) -> List[Task]:
        """
        Retrieve all tasks in the system.

        Returns:
            List[Task]: A list of all task objects, sorted by ID
        """
        return sorted(self._tasks.values(), key=lambda t: t.id)

    def update_task(
        self, task_id: int, title: Optional[str] = None, description: Optional[str] = None
    ) -> Task:
        """
        Update an existing task with new values.

        Args:
            task_id (int): The ID of the task to update
            title (str, optional): New title for the task
            description (str, optional): New description for the task

        Returns:
            Task: The updated task object

        Raises:
            ValueError: If task ID doesn't exist or title is empty
        """
        self._validate_task_exists(task_id)
        self._validate_title(title)

        task = self._tasks[task_id]

        # Update only the fields that were provided
        if title is not None:
            task.title = title.strip()
        if description is not None:
            task.description = description

        return task

    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task by its ID.

        Args:
            task_id (int): The ID of the task to delete

        Returns:
            bool: True if the task was deleted, False if it didn't exist

        Raises:
            ValueError: If task ID doesn't exist
        """
        self._validate_task_exists(task_id)
        del self._tasks[task_id]
        return True

    def toggle_task_completion(self, task_id: int) -> Task:
        """
        Toggle the completion status of a task.

        Args:
            task_id (int): The ID of the task to toggle

        Returns:
            Task: The updated task object with toggled completion status

        Raises:
            ValueError: If task ID doesn't exist
        """
        self._validate_task_exists(task_id)
        task = self._tasks[task_id]
        task.toggle_completion()
        return task

    @property
    def next_available_id(self) -> int:
        """Get the next available ID for a new task."""
        return self._next_id

    def has_task(self, task_id: int) -> bool:
        """
        Check if a task with the given ID exists.

        Args:
            task_id (int): The ID to check

        Returns:
            bool: True if task exists, False otherwise
        """
        return task_id in self._tasks