from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from typing import List, Optional
from ...models.tag import Tag
from ...services.tag_service import TagService
from ...core.auth import get_current_user
from ...models.user import User
from ...core.database import get_db_session


router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/", response_model=List[Tag])
def list_tags(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session)
) -> List[Tag]:
    """
    Get all tags for the current user.
    Enforces user isolation by filtering by current user's ID.
    """
    try:
        tags = TagService.get_user_tags(session, current_user.id)
        return tags
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while retrieving tags"
        )


@router.post("/", response_model=Tag)
def create_tag(
    name: str = Query(..., min_length=1, max_length=50, description="Tag name (1-50 chars, alphanumeric + spaces/hyphens/underscores)"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session)
) -> Tag:
    """
    Create a new tag for the current user.
    Validates tag format and enforces user isolation.
    """
    # Validate tag format: alphanumeric, spaces, hyphens, underscores only
    import re
    if not re.match(r'^[a-zA-Z0-9\s\-_]+$', name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag name can only contain letters, numbers, spaces, hyphens, and underscores"
        )
    
    try:
        # Check if tag already exists for this user
        existing_tag = TagService.get_tag_by_name(session, name, current_user.id)
        if existing_tag:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Tag with this name already exists for this user"
            )
        
        tag = TagService.create_tag(session, name, current_user.id)
        return tag
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while creating tag"
        )


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(
    tag_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session)
) -> None:
    """
    Delete a specific tag for the current user.
    Enforces user isolation by verifying user owns the tag.
    """
    try:
        success = TagService.delete_tag(session, tag_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found or does not belong to current user"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while deleting tag"
        )
