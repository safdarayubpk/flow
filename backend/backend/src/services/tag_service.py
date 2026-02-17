from sqlmodel import Session, select, desc
from fastapi import HTTPException, status
from typing import List, Optional
from src.models.tag import Tag, TagCreate, TagUpdate
from src.core.isolation import ensure_user_owns_resource, get_user_resources
from datetime import datetime, timezone


class TagService:
    """
    Service class for tag-related operations with user isolation enforcement.
    """

    @staticmethod
    def create_tag(*, session: Session, tag_create: TagCreate, user_id: str) -> Tag:
        """
        Create a new tag with the provided details and assign it to the user.
        This implements user isolation by assigning the tag to the current user.
        """
        # Check if tag with this name already exists for this user
        existing_tag = session.exec(
            select(Tag).where(Tag.name == tag_create.name, Tag.user_id == user_id)
        ).first()

        if existing_tag:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tag with this name already exists for the user"
            )

        # Create new tag with user_id assignment
        db_tag = Tag(
            name=tag_create.name,
            color=tag_create.color,
            user_id=user_id
        )

        session.add(db_tag)
        session.commit()
        session.refresh(db_tag)

        return db_tag

    @staticmethod
    def get_user_tags(*, session: Session, user_id: str) -> List[Tag]:
        """
        Get all tags that belong to the specified user.
        This implements user isolation by filtering by user_id.
        """
        # Use the isolation helper to get user's resources
        return get_user_resources(session, Tag, user_id)

    @staticmethod
    def get_tag_by_id(*, session: Session, tag_id: int, user_id: str) -> Tag:
        """
        Get a specific tag by ID, ensuring it belongs to the user.
        This implements user isolation.
        """
        # Use the isolation helper to ensure user owns the resource
        return ensure_user_owns_resource(session, Tag, tag_id, user_id)

    @staticmethod
    def update_tag(*, session: Session, tag_id: int, tag_update: TagUpdate, user_id: str) -> Tag:
        """
        Update a tag, ensuring it belongs to the user.
        This implements user isolation.
        """
        # First, verify that the user owns this tag
        tag = ensure_user_owns_resource(session, Tag, tag_id, user_id)

        # Update only the fields that are provided
        update_data = tag_update.dict(exclude_unset=True)

        # Update the tag with the new data
        for field, value in update_data.items():
            setattr(tag, field, value)

        # Update the updated_at timestamp
        tag.updated_at = datetime.now(timezone.utc)

        session.add(tag)
        session.commit()
        session.refresh(tag)

        return tag

    @staticmethod
    def delete_tag(*, session: Session, tag_id: int, user_id: str) -> bool:
        """
        Delete a tag, ensuring it belongs to the user.
        This implements user isolation.
        """
        # First, verify that the user owns this tag
        tag = ensure_user_owns_resource(session, Tag, tag_id, user_id)

        session.delete(tag)
        session.commit()

        return True