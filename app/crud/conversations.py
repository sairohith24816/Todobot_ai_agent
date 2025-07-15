from sqlmodel import select
from typing import List
from app.core.database import get_session
from app.models.database import ConversationHistory, MessageRole

def save_message(user_id: int, role: MessageRole, content: str) -> ConversationHistory:
    """Save a message to conversation history"""
    with get_session() as session:
        message = ConversationHistory(
            user_id=user_id,
            role=role,
            content=content
        )
        session.add(message)
        session.commit()
        session.refresh(message)
        return message

def get_conversation_history(user_id: int, limit: int = 10) -> List[ConversationHistory]:
    """Get conversation history for a user"""
    with get_session() as session:
        statement = select(ConversationHistory).where(
            ConversationHistory.user_id == user_id
        ).order_by(ConversationHistory.timestamp.desc()).limit(limit)
        return list(reversed(list(session.exec(statement))))
