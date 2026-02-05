from sqlmodel import Field, SQLModel
from datetime import datetime
from typing import Optional


class Tag(SQLModel, table=True):
    """
    Tag model representing categories/labels that can be applied to tasks for organization.
    Each tag is associated with a specific user to maintain isolation.
    This model is kept for potential future use of normalized tag storage.
    Currently, tags are stored as JSON in the Task model for simplicity.
    """
    id: int = Field(primary_key=True)
    name: str = Field(
        min_length=1,
        max_length=50,
        description="Tag name (1-50 characters, alphanumeric + spaces/hyphens/underscores only)"
    )
    user_id: str = Field(
        index=True,
        description="Foreign key linking tag to specific user"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)