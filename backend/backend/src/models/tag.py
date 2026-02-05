from sqlmodel import SQLModel, Field, Column
from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime


class TagBase(SQLModel):
    """
    Base class for Tag model with common fields.
    This implements the Tag entity for categorizing tasks.
    """
    name: str = Field(min_length=1, max_length=50)  # Required, 1-50 characters
    color: Optional[str] = Field(default="#007bff", max_length=7)  # Default blue color in hex


class Tag(TagBase, table=True):
    """
    Tag model representing a category that can be associated with tasks.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)  # Foreign key to user, indexed for performance
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), onupdate=datetime.utcnow)
    )


class TagCreate(TagBase):
    """Schema for creating a new tag"""
    name: str = Field(min_length=1, max_length=50)  # Required, 1-50 characters


class TagUpdate(SQLModel):
    """Schema for updating a tag"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    color: Optional[str] = Field(default=None, max_length=7)


class TagRead(TagBase):
    """Schema for reading tag data"""
    id: int
    user_id: str

    class Config:
        from_attributes = True