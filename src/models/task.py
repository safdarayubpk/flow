from sqlmodel import SQLModel, Field, Column, Relationship
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING, Dict, Any
from sqlalchemy import DateTime, JSON
from typing_extensions import Literal
from src.models.user import User


if TYPE_CHECKING:
    from .tag import Tag


class TaskBase(SQLModel):
    """
    Base class for Task model with common fields.
    This implements the Task entity per data-model.md specification with soft delete per ADR-003.
    Extended with advanced features: priority, tags, due_date, recurrence_rule, reminder_enabled
    """
    title: str = Field(min_length=1, max_length=200)  # Required, 1-200 characters
    description: Optional[str] = Field(default=None)  # Optional description
    completed: bool = Field(default=False)  # Default to false
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), onupdate=datetime.utcnow)
    )
    # Soft delete field per ADR-003
    deleted_at: Optional[datetime] = Field(default=None)

    # Extended fields for advanced features
    priority: Optional[str] = Field(
        default=None,
        index=True,
        description="Priority level (high, medium, low) with index for fast queries"
    )
    tags: Optional[List[str]] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="List of tags stored as JSON array"
    )
    due_date: Optional[datetime] = Field(
        default=None,
        index=True,
        description="Due date and time with index for fast queries"
    )
    recurrence_rule: Optional[str] = Field(
        default=None,
        description="RRULE string for recurrence pattern"
    )
    reminder_enabled: bool = Field(
        default=False,
        description="Whether to enable reminders for this task"
    )


class Task(TaskBase, table=True):
    """
    Task model representing a todo item with id, user_id (foreign key reference),
    title (1-200 chars), optional description, completion status (boolean),
    and timestamps (created_at, updated_at).

    This implements soft delete per ADR-003 by including a deleted_at field.
    Extended with advanced features: priority, tags, due_date, recurrence_rule, reminder_enabled
    """
    # Enforces multi-user isolation via user_id
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, foreign_key="user.id")  # Foreign key to user, indexed for performance

    # Relationship back-reference to user
    user: "User" = Relationship(back_populates="tasks")


class TaskCreate(TaskBase):
    """Schema for creating a new task with advanced features"""
    title: str = Field(min_length=1, max_length=200)  # Required, 1-200 characters
    priority: Optional[str] = Field(
        default=None,
        description="Priority level (high, medium, low)"
    )
    tags: Optional[List[str]] = Field(
        default_factory=list,
        description="List of tags to associate with the task"
    )
    due_date: Optional[datetime] = Field(
        default=None,
        description="Due date and time for the task"
    )
    recurrence_rule: Optional[str] = Field(
        default=None,
        description="RRULE string for recurrence pattern"
    )
    reminder_enabled: bool = Field(
        default=False,
        description="Whether to enable reminders for this task"
    )


class TaskUpdate(SQLModel):
    """Schema for updating a task with advanced features"""
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[str] = Field(
        default=None,
        description="Priority level (high, medium, low)"
    )
    tags: Optional[List[str]] = Field(
        default=None,
        description="List of tags to associate with the task"
    )
    due_date: Optional[datetime] = Field(
        default=None,
        description="Due date and time for the task"
    )
    recurrence_rule: Optional[str] = Field(
        default=None,
        description="RRULE string for recurrence pattern"
    )
    reminder_enabled: Optional[bool] = Field(
        default=None,
        description="Whether to enable reminders for this task"
    )


class TaskRead(TaskBase):
    """Schema for reading task data"""
    id: int
    user_id: str

    class Config:
        from_attributes = True