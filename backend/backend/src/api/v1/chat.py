import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

logger = logging.getLogger(__name__)

from src.core.auth import get_current_user
from src.core.database import get_session
from src.models.user import User
from src.models.conversation import Conversation
from src.services.conversation_service import ConversationService
from src.core.agents import process_chat_request


class ChatRequest(BaseModel):
    conversation_id: Optional[int] = None
    message: str


class ChatResponse(BaseModel):
    conversation_id: int
    response: str
    tool_calls: Optional[list] = []


router = APIRouter()


@router.post("/", response_model=ChatResponse)
def chat_endpoint(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Main chat endpoint that handles conversation with the AI assistant.
    """
    try:
        # If no conversation ID is provided, create a new conversation
        if request.conversation_id is None:
            conversation = ConversationService.create_conversation(
                session=session,
                user_id=current_user.id
            )
            conversation_id = conversation.id
        else:
            # Verify that the conversation belongs to the current user
            conversation = ConversationService.get_conversation_by_id(
                session=session,
                conversation_id=request.conversation_id,
                user_id=current_user.id
            )
            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found or does not belong to user"
                )
            conversation_id = conversation.id

        # Add user message to the conversation
        ConversationService.add_message_to_conversation(
            session=session,
            conversation_id=conversation_id,
            user_id=current_user.id,
            role="user",
            content=request.message
        )

        # Process the message with the AI agent
        ai_response, tool_calls = process_chat_request(
            user_id=current_user.id,
            conversation_id=conversation_id,
            user_message=request.message,
            session=session
        )

        # Add AI response to the conversation
        ConversationService.add_message_to_conversation(
            session=session,
            conversation_id=conversation_id,
            user_id=current_user.id,  # This refers to the user ID for validation
            role="assistant",
            content=ai_response
        )

        return ChatResponse(
            conversation_id=conversation_id,
            response=ai_response,
            tool_calls=tool_calls
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error("Chat processing error: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during chat processing. Please try again."
        )


@router.get("/conversations", response_model=list[Dict[str, Any]])
def list_user_conversations(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get all conversations for the current user.
    """
    try:
        conversations = ConversationService.get_user_conversations(
            session=session,
            user_id=current_user.id
        )

        result = []
        for conv in conversations:
            # Get the last message to show preview
            messages = ConversationService.get_messages_for_conversation(
                session=session,
                conversation_id=conv.id,
                user_id=current_user.id
            )

            last_message = messages[-1] if messages else None

            result.append({
                "id": conv.id,
                "created_at": conv.created_at.isoformat() if hasattr(conv.created_at, 'isoformat') else str(conv.created_at),
                "updated_at": conv.updated_at.isoformat() if hasattr(conv.updated_at, 'isoformat') else str(conv.updated_at),
                "last_message": last_message.content if last_message else "",
                "last_message_at": last_message.created_at.isoformat() if last_message and hasattr(last_message.created_at, 'isoformat') else str(last_message.created_at) if last_message else None
            })

        return result
    except Exception as e:
        logger.error("Error fetching conversations: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching conversations."
        )


@router.get("/conversations/{conversation_id}", response_model=Dict[str, Any])
def get_conversation_detail(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get details of a specific conversation with all its messages.
    """
    try:
        # Verify conversation belongs to user
        conversation = ConversationService.get_conversation_by_id(
            session=session,
            conversation_id=conversation_id,
            user_id=current_user.id
        )

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found or does not belong to user"
            )

        # Get all messages in the conversation
        messages = ConversationService.get_messages_for_conversation(
            session=session,
            conversation_id=conversation_id,
            user_id=current_user.id
        )

        message_list = []
        for msg in messages:
            message_list.append({
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat() if hasattr(msg.created_at, 'isoformat') else str(msg.created_at)
            })

        return {
            "id": conversation.id,
            "user_id": conversation.user_id,
            "created_at": conversation.created_at.isoformat() if hasattr(conversation.created_at, 'isoformat') else str(conversation.created_at),
            "updated_at": conversation.updated_at.isoformat() if hasattr(conversation.updated_at, 'isoformat') else str(conversation.updated_at),
            "messages": message_list
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error fetching conversation details: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching conversation details."
        )