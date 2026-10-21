"""Async database engine and session factory.

Provides the FastAPI dependency (``get_db``) that request handlers use to
get a database session, and the shared ``AsyncSession`` factory that other
parts of the app (Celery tasks, scripts) can use outside of a request.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.db.config import get_database_settings

settings = get_database_settings()

engine = create_async_engine(
    settings.async_database_url,
    pool_pre_ping=True,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    pool_recycle=settings.db_pool_recycle_seconds,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: yields a session, closing it after the request."""
    async with AsyncSessionLocal() as session:
        yield session
