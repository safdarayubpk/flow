from sqlmodel import Session, select
from typing import List, Optional
from ..models.tag import Tag
from ..models.user import User


class TagService:
    """
    Service class for handling tag management operations including
    creating, updating, and querying tags with user isolation.
    """

    @staticmethod
    def create_tag(session: Session, name: str, user_id: str) -> Tag:
        """
        Create a new tag for a specific user.
        """
        db_tag = Tag(name=name, user_id=user_id)
        session.add(db_tag)
        session.commit()
        session.refresh(db_tag)

        return db_tag

    @staticmethod
    def get_user_tags(session: Session, user_id: str) -> List[Tag]:
        """
        Get all tags for a specific user (enforces user isolation).
        """
        query = select(Tag).where(Tag.user_id == user_id)
        return session.exec(query).all()

    @staticmethod
    def get_tag_by_name(session: Session, name: str, user_id: str) -> Optional[Tag]:
        """
        Get a tag by name for a specific user (enforces user isolation).
        """
        query = select(Tag).where(
            Tag.name == name,
            Tag.user_id == user_id
        )
        return session.exec(query).first()

    @staticmethod
    def delete_tag(session: Session, tag_id: int, user_id: str) -> bool:
        """
        Delete a tag for a specific user (enforces user isolation).
        """
        db_tag = session.get(Tag, tag_id)
        if not db_tag or db_tag.user_id != user_id:
            return False

        session.delete(db_tag)
        session.commit()
        return True
