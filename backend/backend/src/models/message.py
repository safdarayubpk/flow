from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .user import User
    from .conversation import Conversation


class MessageBase(SQLModel):
    conversation_id: int = Field(foreign_key="conversation.id")
    user_id: str = Field(foreign_key="user.id")
    role: str  # "user" or "assistant"
    content: str


class Message(MessageBase, table=True):
    """
    Represents a message in a chat conversation.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: "User" = Relationship(back_populates="messages")
    conversation: "Conversation" = Relationship(back_populates="messages")


class MessageCreate(MessageBase):
    """Schema for creating a new message"""
    role: str  # "user" or "assistant"
    content: str


class MessageUpdate(SQLModel):
    """Schema for updating a message"""
    role: Optional[str] = None
    content: Optional[str] = None


class MessageRead(MessageBase):
    """
    Read model for Message without sensitive data.
    """
    id: int
    created_at: datetime