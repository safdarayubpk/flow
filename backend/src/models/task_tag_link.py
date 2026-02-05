from sqlmodel import SQLModel, Field
from typing import Optional


class TaskTagLink(SQLModel, table=True):
    """
    Link table for the many-to-many relationship between Task and Tag.
    """
    task_id: Optional[int] = Field(default=None, foreign_key="task.id", primary_key=True)
    tag_id: Optional[int] = Field(default=None, foreign_key="tag.id", primary_key=True)