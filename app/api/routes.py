from fastapi import APIRouter, HTTPException
from typing import List
from app.api.schemas import (
    UserCreate, UserResponse, TodoCreate, TodoResponse, 
    MessageRequest, MessageResponse, ConversationResponse, TodoStatsResponse
)
from app.crud.users import create_user, get_user_by_name, get_all_users, get_user_by_id, update_user_last_active
from app.crud.todos import create_todo, get_user_todos, complete_todo, delete_todo, get_todo_stats
from app.crud.conversations import get_conversation_history

router = APIRouter()

# Agent will be initialized when needed
agent = None

def get_agent():
    """Get or create agent instance"""
    global agent
    if agent is None:
        import os
        from app.core.agent import TodoAgent
        
        GEMINI_API_KEY = os.getenv("GEMINI_API")
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API key not found in environment variables")
        
        agent = TodoAgent(GEMINI_API_KEY)
    return agent

# User endpoints
@router.post("/users", response_model=UserResponse)
def create_new_user(user: UserCreate):
    """Create a new user"""
    existing_user = get_user_by_name(user.name)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    new_user = create_user(user.name)
    return new_user

@router.get("/users", response_model=List[UserResponse])
def list_users():
    """Get all users"""
    return get_all_users()

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    """Get user by ID"""
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Todo endpoints
@router.post("/users/{user_id}/todos", response_model=TodoResponse)
def create_user_todo(user_id: int, todo: TodoCreate):
    """Create a new todo for user"""
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_todo = create_todo(user_id, todo.task)
    return new_todo

@router.get("/users/{user_id}/todos", response_model=List[TodoResponse])
def list_user_todos(user_id: int):
    """Get all todos for user"""
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return get_user_todos(user_id)

@router.put("/users/{user_id}/todos/{todo_id}/complete")
def complete_user_todo(user_id: int, todo_id: int):
    """Mark todo as completed"""
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    success = complete_todo(todo_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Todo not found or already completed")
    
    return {"message": "Todo marked as completed"}

@router.delete("/users/{user_id}/todos/{todo_id}")
def delete_user_todo(user_id: int, todo_id: int):
    """Delete a todo"""
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    success = delete_todo(todo_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    return {"message": "Todo deleted"}

@router.get("/users/{user_id}/todos/stats", response_model=TodoStatsResponse)
def get_user_todo_stats(user_id: int):
    """Get todo statistics for user"""
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    stats = get_todo_stats(user_id)
    return stats

# Conversation endpoints
@router.get("/users/{user_id}/conversations", response_model=List[ConversationResponse])
def get_user_conversations(user_id: int, limit: int = 20):
    """Get conversation history for user"""
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    conversations = get_conversation_history(user_id, limit)
    return [
        ConversationResponse(
            id=conv.id,
            role=conv.role.value,
            content=conv.content,
            timestamp=conv.timestamp
        )
        for conv in conversations
    ]

# Chat endpoint
@router.post("/users/{user_id}/chat", response_model=MessageResponse)
def chat_with_agent(user_id: int, message: MessageRequest):
    """Send message to AI agent"""
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update user last active
    update_user_last_active(user_id)
    
    # Get response from agent
    agent_instance = get_agent()
    response = agent_instance.chat(message.message, user_id, user.name)
    
    return MessageResponse(response=response)
