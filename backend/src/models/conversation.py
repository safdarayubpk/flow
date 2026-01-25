from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .user import User
    from .message import Message


class ConversationBase(SQLModel):
    user_id: str = Field(foreign_key="user.id")


class Conversation(ConversationBase, table=True):
    """
    Represents a chat conversation between user and AI assistant.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: "User" = Relationship(back_populates="conversations")
    messages: list["Message"] = Relationship(back_populates="conversation")


class ConversationCreate(ConversationBase):
    """Schema for creating a new conversation"""
    pass


class ConversationUpdate(SQLModel):
    """Schema for updating a conversation"""
    pass


class ConversationRead(ConversationBase):
    """
    Read model for Conversation without sensitive data.
    """
    id: int
    created_at: datetime
    updated_at: datetime