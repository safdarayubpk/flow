from sqlmodel import SQLModel, Field, Column
from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime
from src.models.user import User


class TaskBase(SQLModel):
    """
    Base class for Task model with common fields.
    This implements the Task entity per data-model.md specification with soft delete per ADR-003.
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


class Task(TaskBase, table=True):
    """
    Task model representing a todo item with id, user_id (foreign key reference),
    title (1-200 chars), optional description, completion status (boolean),
    and timestamps (created_at, updated_at).

    This implements soft delete per ADR-003 by including a deleted_at field.
    """
    # Enforces multi-user isolation via user_id
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)  # Foreign key to user, indexed for performance


class TaskCreate(TaskBase):
    """Schema for creating a new task"""
    title: str = Field(min_length=1, max_length=200)  # Required, 1-200 characters


class TaskUpdate(SQLModel):
    """Schema for updating a task"""
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    completed: Optional[bool] = None


class TaskRead(TaskBase):
    """Schema for reading task data"""
    id: int
    user_id: str

    class Config:
        from_attributes = True