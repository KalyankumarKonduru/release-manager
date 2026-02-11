"""Database configuration and utilities."""

import logging
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.models.base import Base

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages async database engine and session factory."""

    def __init__(self):
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker] = None

    async def initialize(self) -> None:
        """Initialize database engine and session factory."""
        self._engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DB_ECHO,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
        )
        self._session_factory = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        logger.info("Database engine initialized")

    async def create_tables(self) -> None:
        """Create all tables from models."""
        if self._engine is None:
            raise RuntimeError("Database not initialized")
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created")

    async def close(self) -> None:
        """Close database engine."""
        if self._engine is not None:
            await self._engine.dispose()
            logger.info("Database engine closed")

    def get_session(self) -> AsyncSession:
        """Get a new async session."""
        if self._session_factory is None:
            raise RuntimeError("Database not initialized")
        return self._session_factory()


# Global database manager instance
db = DatabaseManager()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency."""
    async with db.get_session() as session:
        try:
            yield session
        finally:
            await session.close()
