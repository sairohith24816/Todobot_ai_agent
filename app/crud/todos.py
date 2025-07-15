from sqlmodel import select
from typing import List
from app.core.database import get_session
from app.models.database import Todo
from datetime import datetime

def create_todo(user_id: int, task: str) -> Todo:
    """Create a new todo"""
    with get_session() as session:
        todo = Todo(user_id=user_id, task=task)
        session.add(todo)
        session.commit()
        session.refresh(todo)
        return todo

def get_user_todos(user_id: int) -> List[Todo]:
    """Get all todos for a user"""
    with get_session() as session:
        statement = select(Todo).where(Todo.user_id == user_id).order_by(Todo.created_at.desc())
        return list(session.exec(statement))

def get_todo_by_id(todo_id: int, user_id: int) -> Todo:
    """Get todo by ID for a specific user"""
    with get_session() as session:
        statement = select(Todo).where(Todo.id == todo_id, Todo.user_id == user_id)
        return session.exec(statement).first()

def complete_todo(todo_id: int, user_id: int) -> bool:
    """Mark todo as completed"""
    with get_session() as session:
        todo = session.exec(
            select(Todo).where(Todo.id == todo_id, Todo.user_id == user_id)
        ).first()
        
        if todo and not todo.completed:
            todo.completed = True
            todo.completed_at = datetime.now()
            session.add(todo)
            session.commit()
            return True
        return False

def delete_todo(todo_id: int, user_id: int) -> bool:
    """Delete a todo"""
    with get_session() as session:
        todo = session.exec(
            select(Todo).where(Todo.id == todo_id, Todo.user_id == user_id)
        ).first()
        
        if todo:
            session.delete(todo)
            session.commit()
            return True
        return False

def get_todo_stats(user_id: int) -> dict:
    """Get todo statistics for a user"""
    todos = get_user_todos(user_id)
    total = len(todos)
    completed = len([todo for todo in todos if todo.completed])
    pending = total - completed
    
    return {
        "total": total,
        "completed": completed,
        "pending": pending
    }
