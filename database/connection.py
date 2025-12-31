from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
import logging
from config import DATABASE_URL
from .models import Base

logger = logging.getLogger(__name__)

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
Session = scoped_session(sessionmaker(bind=engine))


def init_db():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


@contextmanager
def get_session():
    """Provide a transactional scope for database operations"""
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        session.close()


def get_db():
    """Get database session for dependency injection"""
    return Session()
