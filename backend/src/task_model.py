"""
Task data model for the Console Todo App.

This module defines the Task class that represents a single task
with all required attributes and validation.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Task:
    """
    Represents a single task in the todo application.

    Attributes:
        id (int): Unique sequential integer identifier
        title (str): Short text describing the task (required, non-empty)
        description (str): Optional longer text with additional details
        completed (bool): Boolean status indicating if task is done (defaults to false)
        created_at (datetime): Timestamp of creation
    """

    id: int
    title: str
    description: Optional[str] = None
    completed: bool = False
    created_at: datetime = None

    def __post_init__(self):
        """Validate task attributes after initialization."""
        if not self.title or not self.title.strip():
            raise ValueError("Task title must be non-empty")

        if self.id <= 0:
            raise ValueError("Task ID must be a positive integer")

        if self.created_at is None:
            self.created_at = datetime.now()

    @property
    def title_stripped(self) -> str:
        """Return the title with leading/trailing whitespace stripped."""
        return self.title.strip()

    def toggle_completion(self) -> None:
        """Toggle the completion status of the task."""
        self.completed = not self.completed

    def __str__(self) -> str:
        """String representation of the task."""
        status = "[x]" if self.completed else "[ ]"
        desc = f" | {self.description}" if self.description else ""
        return f"{self.id:2} | {status} | {self.title_stripped} | {desc}"

    def __repr__(self) -> str:
        """Detailed string representation of the task."""
        return (
            f"Task(id={self.id}, title='{self.title_stripped}', "
            f"description='{self.description}', completed={self.completed}, "
            f"created_at={self.created_at})"
        )