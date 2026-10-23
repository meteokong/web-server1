"""DocumentQueueService (T095): dispatches async document generation
(T094's Celery task) and reports its status, so callers (T096's upload
trigger, T097/T098's API endpoints) never need to know about Celery
directly.

``LearningDocument.content`` is NOT NULL with a CHECK requiring all 7
chapter keys (see T090/T009) — same constraint DocumentGenerationService
(T093) works around — so a "no content yet" pending row still needs a
placeholder content. ``_PLACEHOLDER_CONTENT`` mirrors T093's exactly.
"""

import uuid
from collections.abc import Callable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.learning_document import LearningDocument
from src.services.task_service import TaskService
from src.tasks.document_generation import generate_document_task

REQUIRED_CHAPTER_KEYS = tuple(f"chapter{i}" for i in range(1, 8))
_PLACEHOLDER_CONTENT = dict.fromkeys(REQUIRED_CHAPTER_KEYS)

# What Celery's `.delay()` returns: an AsyncResult-like object exposing
# `.id`. `dispatch(task_id: str, user_id: str) -> <has .id>`.
Dispatcher = Callable[[str, str], object]


class DocumentQueueService:
    def __init__(self, db: AsyncSession, *, dispatch: Dispatcher | None = None) -> None:
        self.db = db
        self._dispatch = dispatch or generate_document_task.delay

    async def enqueue(self, task_id: uuid.UUID, user_id: uuid.UUID) -> LearningDocument:
        """Create/reuse this task's LearningDocument row, mark it
        "pending", dispatch the Celery generation task, and persist the
        dispatched Celery task id. Raises NotFoundError if the task isn't
        owned by ``user_id`` (via TaskService.get)."""
        await TaskService(self.db).get(task_id, user_id)  # ownership + 404

        document = await self._get_or_create_document(task_id)
        document.generation_status = "pending"
        document.generation_error = None
        await self.db.flush()

        async_result = self._dispatch(str(task_id), str(user_id))
        document.celery_task_id = async_result.id
        await self.db.flush()
        return document

    async def get_status(self, task_id: uuid.UUID, user_id: uuid.UUID) -> dict:
        """Return this task's document-generation status. If generation
        hasn't been triggered yet (no LearningDocument row), reports
        "pending" with the remaining fields null rather than raising -
        that's a valid, expected state. Raises NotFoundError if the task
        isn't owned by ``user_id``."""
        await TaskService(self.db).get(task_id, user_id)  # ownership + 404

        document = await self._get_document(task_id)
        if document is None:
            return {
                "task_id": task_id,
                "generation_status": "pending",
                "generation_error": None,
                "generation_started_at": None,
                "generation_completed_at": None,
            }

        return {
            "task_id": task_id,
            "generation_status": document.generation_status,
            "generation_error": document.generation_error,
            "generation_started_at": document.generation_started_at,
            "generation_completed_at": document.generation_completed_at,
        }

    async def get_document(self, task_id: uuid.UUID, user_id: uuid.UUID) -> dict:
        """Return this task's generation status + content (T097's API
        contract). ``content`` is only ever non-null when
        generation_status == "completed" - while pending/in_progress/failed
        the row holds only placeholder content (T093/T095's
        _PLACEHOLDER_CONTENT), which callers must never see as real data.
        Like get_status(), reports "pending" + null content rather than
        404 when no LearningDocument row exists yet. Raises NotFoundError
        if the task isn't owned by ``user_id``."""
        await TaskService(self.db).get(task_id, user_id)  # ownership + 404

        document = await self._get_document(task_id)
        if document is None:
            return {
                "task_id": task_id,
                "generation_status": "pending",
                "generation_error": None,
                "content": None,
            }

        content = document.content if document.generation_status == "completed" else None
        return {
            "task_id": task_id,
            "generation_status": document.generation_status,
            "generation_error": document.generation_error,
            "content": content,
        }

    async def _get_document(self, task_id: uuid.UUID) -> LearningDocument | None:
        result = await self.db.execute(
            select(LearningDocument).where(LearningDocument.task_id == task_id)
        )
        return result.scalar_one_or_none()

    async def _get_or_create_document(self, task_id: uuid.UUID) -> LearningDocument:
        document = await self._get_document(task_id)
        if document is None:
            document = LearningDocument(task_id=task_id, content=dict(_PLACEHOLDER_CONTENT))
            self.db.add(document)
            await self.db.flush()
        return document
