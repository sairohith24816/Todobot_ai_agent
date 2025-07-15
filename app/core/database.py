from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "sqlite:///todo.db"
engine = create_engine(DATABASE_URL)

def init_db():
    """Initialize database tables"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Get database session"""
    return Session(engine)
