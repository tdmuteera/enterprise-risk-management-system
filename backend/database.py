"""
Database configuration using SQLAlchemy 2.x with async support.
Uses asyncpg driver for PostgreSQL.
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import text
import logging
from config import settings

# Use the project"s single source-of-truth ORM definitions
from models_complete import Base

logger = logging.getLogger(__name__)


async def init_db_engine() -> AsyncEngine:
    """
    Create and configure async SQLAlchemy engine.
    
    Returns:
        AsyncEngine: Configured async database engine
    """
    engine = create_async_engine(
        settings.db_url,
        echo=settings.effective_debug,
        future=True,
        pool_pre_ping=True,
        poolclass=NullPool if settings.effective_debug else None,
    )
    logger.info(f"Database engine created for {settings.db_url}")
    return engine


async def get_session(engine: AsyncEngine):
    """
    Create async session factory.
    
    Args:
        engine: AsyncEngine instance
        
    Returns:
        sessionmaker: Configured async session factory
    """
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
    return async_session


async def check_db_connection(engine: AsyncEngine) -> bool:
    """
    Verify database connectivity.
    
    Args:
        engine: AsyncEngine instance
        
    Returns:
        bool: True if connected, False otherwise
    """
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("✓ Database connection verified")
        return True
    except Exception as e:
        logger.error(f"✗ Database connection failed: {str(e)}")
        return False


# Dependency for FastAPI routes
async def get_db(session_factory):
    """
    Dependency injection for database sessions.
    
    Usage in routes:
        async def some_route(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
