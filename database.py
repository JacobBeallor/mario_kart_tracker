from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from config import config
from models import Base

# Create engine
engine = create_engine(config.database_url)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize the database, creating all tables."""
    Base.metadata.create_all(bind=engine)

def get_db() -> Session:
    """Get a new database session."""
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.close()
        raise e

@contextmanager
def get_db_context():
    """Context manager for database sessions."""
    db = get_db()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()