from sqlmodel import Session, select
from fastapi import HTTPException, status
from typing import Optional
from src.models.user import User, UserCreate
from src.core.security import get_password_hash, verify_password
from datetime import timedelta


class UserService:
    """
    Service class for user-related operations like registration and authentication.
    """

    @staticmethod
    def create_user(*, session: Session, user_create: UserCreate) -> User:
        """
        Create a new user with the provided details.
        """
        # Check if user with this email already exists
        existing_user = session.exec(select(User).where(User.email == user_create.email)).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists"
            )

        # Verify password confirmation matches
        if user_create.password != user_create.password_confirm:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match"
            )

        # Create new user
        db_user = User(
            email=user_create.email,
            password_hash=get_password_hash(user_create.password)
        )

        session.add(db_user)
        session.commit()
        session.refresh(db_user)

        return db_user

    @staticmethod
    def get_user_by_email(*, session: Session, email: str) -> Optional[User]:
        """
        Retrieve a user by their email address.
        """
        return session.exec(select(User).where(User.email == email)).first()

    @staticmethod
    def get_user_by_id(*, session: Session, user_id: str) -> Optional[User]:
        """
        Retrieve a user by their ID.
        """
        return session.exec(select(User).where(User.id == user_id)).first()

    @staticmethod
    def authenticate_user(*, session: Session, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user by email and password.
        """
        user = session.exec(select(User).where(User.email == email)).first()
        if not user or not verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against its hash.
        This implements the password verification functionality as required by the spec.
        """
        return verify_password(plain_password, hashed_password)

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt.
        This implements the password hashing functionality as required by the spec.
        """
        return get_password_hash(password)