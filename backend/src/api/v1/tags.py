from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlmodel import Session
from typing import List
from src.services.tag_service import TagService
from src.core.database import get_session
from src.core.auth import get_current_user
from src.models.tag import Tag, TagCreate, TagUpdate, TagRead
from src.models.user import User


router = APIRouter()


@router.get("/", response_model=List[TagRead])
def list_tags(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    """
    Get all tags for the current user.
    This implements user isolation by filtering by current user's ID.
    """
    try:
        # Get all tags for the current user
        tags = TagService.get_user_tags(session=session, user_id=current_user.id)
        return tags
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while retrieving tags"
        )


@router.post("/", response_model=TagRead, status_code=status.HTTP_201_CREATED)
def create_tag(
    tag_create: TagCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Create a new tag for the current user.
    This implements user isolation by assigning the tag to the current user.
    """
    try:
        # Validate tag name length per spec (1-50 characters)
        if len(tag_create.name.strip()) < 1 or len(tag_create.name) > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tag name must be between 1 and 50 characters"
            )

        # Create tag with user_id assignment
        tag = TagService.create_tag(
            session=session,
            tag_create=tag_create,
            user_id=current_user.id
        )
        return tag
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while creating the tag"
        )


@router.get("/{tag_id}", response_model=TagRead)
def get_tag(
    tag_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get a specific tag by ID if it belongs to the current user.
    This implements user isolation by validating ownership.
    """
    try:
        tag = TagService.get_tag_by_id(
            session=session,
            tag_id=tag_id,
            user_id=current_user.id
        )
        return tag
    except HTTPException:
        # Re-raise HTTP exceptions (like 404 for not found)
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while retrieving the tag"
        )


@router.put("/{tag_id}", response_model=TagRead)
def update_tag(
    tag_id: int,
    tag_update: TagUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update an existing tag if it belongs to the current user.
    This implements user isolation by validating ownership.
    """
    try:
        # Validate tag name length if it's being updated
        if tag_update.name is not None:
            if len(tag_update.name.strip()) < 1 or len(tag_update.name) > 50:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Tag name must be between 1 and 50 characters"
                )

        tag = TagService.update_tag(
            session=session,
            tag_id=tag_id,
            tag_update=tag_update,
            user_id=current_user.id
        )
        return tag
    except HTTPException:
        # Re-raise HTTP exceptions (like 404 for not found, 403 for forbidden)
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while updating the tag"
        )


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(
    tag_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete a tag if it belongs to the current user.
    This implements user isolation by validating ownership.
    """
    try:
        # Verify user owns the tag before deletion
        tag = TagService.get_tag_by_id(
            session=session,
            tag_id=tag_id,
            user_id=current_user.id
        )

        # Delete the tag
        success = TagService.delete_tag(
            session=session,
            tag_id=tag_id,
            user_id=current_user.id
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )

        # Return 204 No Content for successful deletion
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException:
        # Re-raise HTTP exceptions (like 404 for not found, 403 for forbidden)
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while deleting the tag"
        )