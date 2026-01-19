from sqlmodel import SQLModel, Field, Column
from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime
from uuid import UUID, uuid4
import hashlib


def generate_user_id():
    """Generate a unique user ID"""
    return str(uuid4())


class UserBase(SQLModel):

    email: str = Field(unique=True, nullable=False, max_length=255, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), onupdate=datetime.utcnow)
    )


class User(UserBase, table=True):
    """
    User model representing a registered user with email, password, and account details managed by Better Auth.
    This follows the specification in data-model.md with fields as required.
    """
    # Enforces multi-user isolation via user_id
    id: str = Field(default_factory=generate_user_id, primary_key=True)  # Using UUID string as primary key
    password_hash: str = Field(nullable=False)  # Hashed password as required by spec


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str  # Plain password that will be hashed
    password_confirm: str  # Confirmation of password


class UserUpdate(SQLModel):
    """Schema for updating user details"""
    email: Optional[str] = None


class UserRead(UserBase):
    """Schema for reading user data (without password)"""
    id: str

    class Config:
        from_attributes = True