from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.now)
    last_active: datetime = Field(default_factory=datetime.now)

class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    task: str
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

class ConversationHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
