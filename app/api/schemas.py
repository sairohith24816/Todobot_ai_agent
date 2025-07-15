from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    name: str

class UserResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    last_active: datetime

class TodoCreate(BaseModel):
    task: str

class TodoResponse(BaseModel):
    id: int
    task: str
    completed: bool
    created_at: datetime
    completed_at: Optional[datetime] = None

class MessageRequest(BaseModel):
    user_id: int
    message: str

class MessageResponse(BaseModel):
    response: str

class ConversationResponse(BaseModel):
    id: int
    role: str
    content: str
    timestamp: datetime

class TodoStatsResponse(BaseModel):
    total: int
    completed: int
    pending: int
