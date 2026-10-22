"""Celery task (T094): async document generation, dispatched from
DocumentQueueService.enqueue() (T095) after a code upload (T096).

DocumentGenerationService.generate() (T093) is async, but Celery workers
invoke tasks in a synchronous context. The task function below is the
thin synchronous Celery entrypoint; it just hands off to ``asyncio.run()``
on the real async logic (``_generate_document``).

Session/engine: this module creates its own AsyncEngine/session factory
rather than reusing src/db/session.py's module-level ``engine`` /
``AsyncSessionLocal``. asyncpg connections are bound to the event loop
that created them (see tests/conftest.py's db_session fixture for the
same reasoning), and a Celery worker calling this task repeatedly -
potentially via asyncio.run() each time, each run getting its own fresh
loop - must not reuse a connection pool tied to a *different* loop (the
FastAPI app's, or a previous task invocation's). A short-lived
engine/session created and disposed within each task invocation sidesteps
that entirely, at the cost of a fresh connection per generation run - an
acceptable trade given these runs are infrequent (once per task) and can
take up to minutes (task_time_limit=5*60 in celery_app.py), so a single
extra connection setup is negligible overhead.

``_run_generation`` is factored out of ``_generate_document`` so it can be
exercised directly against a caller-supplied AsyncSession (e.g. a test's
db_session fixture) without needing a second, independent DB connection -
see tests/integration/test_document_generation_task.py.

No retry at the Celery level (``max_retries=0``): DocumentGenerationService
already retries internally with exponential backoff (up to 3 attempts,
T093) and leaves the LearningDocument row in a terminal state
(generation_status="completed" or "failed") either way by the time it
raises - there is nothing left for Celery to usefully gain by retrying
again on top of that, so the failure is left to propagate (not swallowed)
and simply surfaces as this Celery task's own FAILURE state.
"""

import asyncio
import uuid

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.db.config import get_database_settings
from src.services.ai.gemini_client import GeminiClient
from src.services.document.document_generation_service import DocumentGenerationService
from src.tasks.celery_app import celery_app


async def _run_generation(
    session: AsyncSession,
    task_id: str,
    user_id: str,
    gemini_client: GeminiClient | None = None,
) -> None:
    """Run DocumentGenerationService.generate() on an existing session.
    Does not commit - the caller (``_generate_document`` for the real
    Celery path, or a test fixture) owns the session's lifecycle."""
    service = DocumentGenerationService(session, gemini_client=gemini_client) if gemini_client else DocumentGenerationService(session)
    await service.generate(uuid.UUID(task_id), uuid.UUID(user_id))


async def _generate_document(
    task_id: str,
    user_id: str,
    *,
    gemini_client: GeminiClient | None = None,
) -> None:
    settings = get_database_settings()
    engine = create_async_engine(settings.async_database_url, pool_pre_ping=True)
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)
    try:
        async with session_factory() as session:
            await _run_generation(session, task_id, user_id, gemini_client)
            await session.commit()
    finally:
        await engine.dispose()


@celery_app.task(name="src.tasks.document_generation.generate_document_task", max_retries=0)
def generate_document_task(task_id: str, user_id: str) -> None:
    asyncio.run(_generate_document(task_id, user_id))
