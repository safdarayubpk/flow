from sqlmodel import Session, select
from fastapi import HTTPException, status
from typing import TypeVar, Generic, Type
from src.models.user import User
from src.models.task import Task


T = TypeVar('T')


def ensure_user_owns_resource(
    session: Session,
    resource_class: Type[T],
    resource_id: int,
    user_id: str
) -> T:
    """
    Ensure that the user owns the specified resource.
    This implements ADR-002 for application-level user isolation.

    Args:
        session: Database session
        resource_class: The SQLModel class of the resource (e.g., Task)
        resource_id: ID of the resource to check
        user_id: ID of the user attempting access

    Returns:
        The resource if the user owns it

    Raises:
        HTTPException: If the resource doesn't exist or user doesn't own it
    """
    # Construct query to check if resource belongs to user
    stmt = select(resource_class).where(
        resource_class.user_id == user_id
    ).where(
        resource_class.id == resource_id
    )

    resource = session.exec(stmt).first()

    if not resource:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied - not your resource"
        )

    return resource


def get_user_resources(
    session: Session,
    resource_class: Type[T],
    user_id: str
) -> list[T]:
    """
    Get all resources that belong to a specific user.
    This implements ADR-002 for application-level user isolation.

    Args:
        session: Database session
        resource_class: The SQLModel class of the resource (e.g., Task)
        user_id: ID of the user whose resources to retrieve

    Returns:
        List of resources that belong to the user
    """
    stmt = select(resource_class).where(resource_class.user_id == user_id)
    return session.exec(stmt).all()


def filter_query_by_user(
    session: Session,
    base_query,
    user_id: str,
    resource_class: Type[T]
):
    """
    Apply user filtering to an existing query.
    This implements ADR-002 for application-level user isolation.

    Args:
        session: Database session
        base_query: Base query to filter
        user_id: ID of the user whose resources to access
        resource_class: The SQLModel class of the resource

    Returns:
        Query filtered by user_id
    """
    # This would typically be used in more complex queries
    # For now, we'll return the base query with user filter applied
    return base_query.where(resource_class.user_id == user_id)