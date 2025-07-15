from sqlmodel import select
from typing import List, Optional
from app.core.database import get_session
from app.models.database import User
from datetime import datetime

def create_user(name: str) -> User:
    """Create a new user"""
    with get_session() as session:
        user = User(name=name)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

def get_user_by_name(name: str) -> Optional[User]:
    """Get user by name"""
    with get_session() as session:
        statement = select(User).where(User.name == name)
        return session.exec(statement).first()

def get_user_by_id(user_id: int) -> Optional[User]:
    """Get user by ID"""
    with get_session() as session:
        return session.get(User, user_id)

def get_all_users() -> List[User]:
    """Get all users"""
    with get_session() as session:
        statement = select(User).order_by(User.name)
        return list(session.exec(statement))

def update_user_last_active(user_id: int):
    """Update user's last active timestamp"""
    with get_session() as session:
        user = session.get(User, user_id)
        if user:
            user.last_active = datetime.now()
            session.add(user)
            session.commit()
