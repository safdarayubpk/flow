from sqlmodel import Session, select
from typing import Optional
from datetime import datetime
from src.models.conversation import Conversation, ConversationCreate
from src.models.message import Message, MessageCreate
from src.models.user import User


class ConversationService:
    """
    Service class for managing conversations and messages.
    """

    @staticmethod
    def create_conversation(session: Session, user_id: str) -> Conversation:
        """
        Create a new conversation for a user.
        """
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        return conversation

    @staticmethod
    def get_conversation_by_id(session: Session, conversation_id: int, user_id: str) -> Optional[Conversation]:
        """
        Get a specific conversation by ID for a user.
        """
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        return session.exec(statement).first()

    @staticmethod
    def get_user_conversations(session: Session, user_id: str) -> list[Conversation]:
        """
        Get all conversations for a user.
        """
        statement = select(Conversation).where(Conversation.user_id == user_id)
        return session.exec(statement).all()

    @staticmethod
    def add_message_to_conversation(
        session: Session,
        conversation_id: int,
        user_id: str,
        role: str,
        content: str
    ) -> Message:
        """
        Add a message to a conversation.
        """
        # Verify the conversation belongs to the user
        conversation = ConversationService.get_conversation_by_id(
            session, conversation_id, user_id
        )
        if not conversation:
            raise ValueError("Conversation not found or does not belong to user")

        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=content
        )
        session.add(message)
        session.commit()
        session.refresh(message)
        return message

    @staticmethod
    def get_messages_for_conversation(
        session: Session,
        conversation_id: int,
        user_id: str
    ) -> list[Message]:
        """
        Get all messages for a specific conversation that belongs to the user.
        """
        # Verify conversation belongs to user
        conversation = ConversationService.get_conversation_by_id(
            session, conversation_id, user_id
        )
        if not conversation:
            raise ValueError("Conversation not found or does not belong to user")

        statement = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at)
        return session.exec(statement).all()

    @staticmethod
    def delete_conversation(session: Session, conversation_id: int, user_id: str) -> bool:
        """
        Delete a conversation for a user.
        """
        conversation = ConversationService.get_conversation_by_id(
            session, conversation_id, user_id
        )
        if not conversation:
            return False

        session.delete(conversation)
        session.commit()
        return True