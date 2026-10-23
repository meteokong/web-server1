"""DocumentGenerationService (T093): orchestrates generating a Task's
7-chapter LearningDocument (T090) via Gemini (T091 client, T092 prompts).

Retry policy lives here (not in GeminiClient, see its docstring): research.md
calls for "Exponential backoff up to 3 retries" specifically for document
generation — a Q&A caller would want a different policy.

`LearningDocument.content` is NOT NULL with a CHECK requiring all 7
chapter keys to be present (see T009 migration / T090), so a document row
can only ever exist with that shape — there's no way to persist a
"pending, no content yet" row. `in_progress` is therefore tracked with a
placeholder content (`_PLACEHOLDER_CONTENT`, every chapter key present but
null) until real content overwrites it on success; on failure after all
retries, the row is left with that placeholder content and
generation_status="failed" rather than disappearing (so a caller can see
*that* it failed, and why, without extra schema).
"""

import json
import uuid
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.api.exceptions import NotFoundError, ValidationAppError
from src.models.code_file import CodeFile
from src.models.learning_document import LearningDocument
from src.models.uploaded_code import UploadedCode
from src.services.ai.gemini_client import GeminiAPIError, GeminiClient
from src.services.ai.prompts import (
    SYSTEM_INSTRUCTION,
    CodeFileInput,
    build_document_generation_prompt,
)
from src.services.task_service import TaskService

# research.md ("Retry strategy: Exponential backoff up to 3 retries").
MAX_RETRIES = 3
_BASE_BACKOFF_SECONDS = 1.0

REQUIRED_CHAPTER_KEYS = tuple(f"chapter{i}" for i in range(1, 8))
_PLACEHOLDER_CONTENT = dict.fromkeys(REQUIRED_CHAPTER_KEYS)


class DocumentGenerationError(Exception):
    """Raised when generation fails after exhausting all retries. The
    LearningDocument row is left with generation_status="failed" and
    generation_error set — this exception is only the synchronous
    caller's signal that it didn't succeed."""


class DocumentGenerationService:
    def __init__(
        self,
        db: AsyncSession,
        *,
        gemini_client: GeminiClient | None = None,
        max_retries: int = MAX_RETRIES,
        backoff_seconds: float = _BASE_BACKOFF_SECONDS,
        sleep=None,
    ) -> None:
        self.db = db
        self._gemini_client = gemini_client or GeminiClient()
        self._max_retries = max_retries
        self._backoff_seconds = backoff_seconds
        if sleep is None:
            import time

            sleep = time.sleep
        self._sleep = sleep

    async def generate(self, task_id: uuid.UUID, user_id: uuid.UUID) -> LearningDocument:
        """Generate (or regenerate) the LearningDocument for ``task_id``.

        Raises NotFoundError if the task isn't owned by ``user_id`` or has
        no uploaded code yet. Raises DocumentGenerationError if Gemini
        keeps failing (or keeps returning an invalid/incomplete response)
        after `max_retries` attempts.
        """
        await TaskService(self.db).get(task_id, user_id)  # ownership + 404

        uploaded_code = await self._get_uploaded_code(task_id)
        files = self._read_files(uploaded_code.code_files)

        document = await self._get_or_create_document(task_id)
        document.generation_status = "in_progress"
        document.generation_started_at = _utcnow()
        document.generation_error = None
        await self.db.flush()

        prompt = build_document_generation_prompt(
            files=files,
            language=uploaded_code.detected_language,
            complexity_level=uploaded_code.complexity_level,
        )

        try:
            content = self._generate_with_retry(prompt)
        except GeminiAPIError as exc:
            document.generation_status = "failed"
            document.generation_error = str(exc)
            await self.db.flush()
            raise DocumentGenerationError(str(exc)) from exc

        document.content = content
        document.generation_status = "completed"
        document.generation_completed_at = _utcnow()
        document.generation_error = None
        await self.db.flush()
        return document

    def _generate_with_retry(self, prompt: str) -> dict:
        last_error: GeminiAPIError | None = None
        for attempt in range(self._max_retries):
            try:
                text = self._gemini_client.generate_content(
                    prompt,
                    system_instruction=SYSTEM_INSTRUCTION,
                    response_mime_type="application/json",
                )
                content = json.loads(text)
                _validate_chapters(content)
                return content
            except GeminiAPIError as exc:
                last_error = exc
            except (json.JSONDecodeError, ValidationAppError) as exc:
                last_error = GeminiAPIError(str(exc))

            if attempt < self._max_retries - 1:
                self._sleep(self._backoff_seconds * (2**attempt))

        assert last_error is not None  # loop always runs >= 1 time
        raise last_error

    async def _get_uploaded_code(self, task_id: uuid.UUID) -> UploadedCode:
        result = await self.db.execute(
            select(UploadedCode)
            .where(UploadedCode.task_id == task_id)
            .options(selectinload(UploadedCode.code_files))
        )
        uploaded_code = result.scalar_one_or_none()
        if uploaded_code is None:
            raise NotFoundError("uploaded code not found for this task")
        return uploaded_code

    async def _get_or_create_document(self, task_id: uuid.UUID) -> LearningDocument:
        result = await self.db.execute(
            select(LearningDocument).where(LearningDocument.task_id == task_id)
        )
        document = result.scalar_one_or_none()
        if document is None:
            document = LearningDocument(task_id=task_id, content=dict(_PLACEHOLDER_CONTENT))
            self.db.add(document)
            await self.db.flush()
        return document

    @staticmethod
    def _read_files(code_files: list[CodeFile]) -> list[CodeFileInput]:
        if not code_files:
            raise ValidationAppError("task has no uploaded code files")
        return [
            CodeFileInput(
                file_name=cf.file_path or cf.file_name,
                content=Path(cf.storage_path).read_text(encoding="utf-8", errors="replace"),
            )
            for cf in code_files
        ]


def _validate_chapters(content: dict) -> None:
    if not isinstance(content, dict):
        raise ValidationAppError("Gemini response is not a JSON object")
    missing = [key for key in REQUIRED_CHAPTER_KEYS if key not in content]
    if missing:
        raise ValidationAppError(f"Gemini response missing chapters: {missing}")


def _utcnow() -> datetime:
    return datetime.now(UTC)
