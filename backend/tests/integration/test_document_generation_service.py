"""Integration tests for DocumentGenerationService (T093) — run against the
real database (see tests/conftest.py's db_session fixture) because the
behaviors that matter (LearningDocument persisting, task_id uniqueness,
generation_status transitions) are DB-level guarantees.

Gemini itself is never called: a fake client (matching GeminiClient's
`generate_content` signature) is injected so these tests only exercise
DocumentGenerationService's own orchestration/retry logic.

Every test passes an explicit `upload_root` (pytest tmp_path) to
CodeUploadService so files are never written to the real storage/uploads
directory.
"""

import json

import pytest

from src.api.exceptions import NotFoundError
from src.models.learning_document import LearningDocument
from src.models.user import User
from src.services.ai.gemini_client import GeminiAPIError
from src.services.code_analysis.code_upload_service import CodeUploadService
from src.services.document.document_generation_service import (
    DocumentGenerationError,
    DocumentGenerationService,
)
from src.services.project_service import ProjectService
from src.services.task_service import TaskService
from src.utils.security import hash_password

SAMPLE_CONTENT = {
    "chapter1": {"title": "What This Code Does", "summary": "Adds two numbers."},
    "chapter2": {"title": "Prerequisites Knowledge", "concepts": []},
    "chapter3": {"title": "Code Structure Overview", "flowchart": "", "file_breakdown": {}},
    "chapter4": {"title": "Line-by-Line Explanation", "explanations": []},
    "chapter5": {"title": "Execution Flow Simulation", "steps": []},
    "chapter6": {"title": "Core Concepts Summary", "concepts": []},
    "chapter7": {"title": "Common Mistakes", "mistakes": []},
}


class _FakeGeminiClient:
    """Stands in for GeminiClient: raises `error` for the first
    `fail_count` calls, then returns each of `responses` in order."""

    def __init__(self, responses=None, fail_count=0, error=None):
        self._responses = list(responses) if responses is not None else [json.dumps(SAMPLE_CONTENT)]
        self._fail_count = fail_count
        self._error = error or GeminiAPIError("transient failure", code=503)
        self.calls: list[dict] = []

    def generate_content(self, prompt, *, system_instruction=None, response_mime_type=None):
        self.calls.append(
            {
                "prompt": prompt,
                "system_instruction": system_instruction,
                "response_mime_type": response_mime_type,
            }
        )
        if len(self.calls) <= self._fail_count:
            raise self._error
        return self._responses.pop(0)


async def _make_task_with_upload(db_session, email: str, tmp_path, *, content=b"def add(a, b):\n    return a + b\n"):
    user = User(email=email, password_hash=hash_password("correct-horse-123"))
    db_session.add(user)
    await db_session.flush()
    project = await ProjectService(db_session).create(user.id, "Project")
    task = await TaskService(db_session).create(project.id, user.id, "A Task", upload_method="file")
    await CodeUploadService(db_session, upload_root=tmp_path).upload(
        task.id, user.id, "file", files=[("main.py", None, content)]
    )
    return user, task


async def test_generate_creates_completed_document_with_content(db_session, tmp_path):
    user, task = await _make_task_with_upload(db_session, "gen-ok@example.com", tmp_path)
    fake_client = _FakeGeminiClient()
    service = DocumentGenerationService(db_session, gemini_client=fake_client, sleep=lambda _: None)

    document = await service.generate(task.id, user.id)

    assert document.task_id == task.id
    assert document.generation_status == "completed"
    assert document.content == SAMPLE_CONTENT
    assert document.generation_completed_at is not None
    assert document.generation_error is None
    assert len(fake_client.calls) == 1


async def test_generate_passes_detected_language_and_complexity_into_prompt(db_session, tmp_path):
    user, task = await _make_task_with_upload(db_session, "gen-prompt@example.com", tmp_path)
    fake_client = _FakeGeminiClient()
    service = DocumentGenerationService(db_session, gemini_client=fake_client, sleep=lambda _: None)

    await service.generate(task.id, user.id)

    prompt = fake_client.calls[0]["prompt"]
    assert "python" in prompt.lower()
    assert "beginner" in prompt.lower()
    assert fake_client.calls[0]["response_mime_type"] == "application/json"


async def test_generate_retries_on_transient_error_then_succeeds(db_session, tmp_path):
    user, task = await _make_task_with_upload(db_session, "gen-retry@example.com", tmp_path)
    fake_client = _FakeGeminiClient(fail_count=2)  # fails twice, succeeds on 3rd attempt
    service = DocumentGenerationService(db_session, gemini_client=fake_client, sleep=lambda _: None)

    document = await service.generate(task.id, user.id)

    assert document.generation_status == "completed"
    assert len(fake_client.calls) == 3


async def test_generate_marks_failed_after_exhausting_retries(db_session, tmp_path):
    user, task = await _make_task_with_upload(db_session, "gen-fail@example.com", tmp_path)
    fake_client = _FakeGeminiClient(fail_count=10)  # always fails
    service = DocumentGenerationService(db_session, gemini_client=fake_client, sleep=lambda _: None)

    with pytest.raises(DocumentGenerationError):
        await service.generate(task.id, user.id)

    assert len(fake_client.calls) == 3  # MAX_RETRIES

    result = await _get_document(db_session, task.id)
    assert result.generation_status == "failed"
    assert result.generation_error is not None


async def test_generate_raises_not_found_when_task_has_no_uploaded_code(db_session):
    user = User(email="gen-no-upload@example.com", password_hash=hash_password("correct-horse-123"))
    db_session.add(user)
    await db_session.flush()
    project = await ProjectService(db_session).create(user.id, "Project")
    task = await TaskService(db_session).create(project.id, user.id, "A Task", upload_method="file")

    service = DocumentGenerationService(
        db_session, gemini_client=_FakeGeminiClient(), sleep=lambda _: None
    )

    with pytest.raises(NotFoundError):
        await service.generate(task.id, user.id)


async def test_generate_raises_not_found_for_another_users_task(db_session, tmp_path):
    _owner, task = await _make_task_with_upload(db_session, "gen-owner@example.com", tmp_path)
    other_user = User(email="gen-other@example.com", password_hash=hash_password("correct-horse-123"))
    db_session.add(other_user)
    await db_session.flush()

    service = DocumentGenerationService(
        db_session, gemini_client=_FakeGeminiClient(), sleep=lambda _: None
    )

    with pytest.raises(NotFoundError):
        await service.generate(task.id, other_user.id)


async def test_generate_wraps_invalid_json_response_and_retries(db_session, tmp_path):
    user, task = await _make_task_with_upload(db_session, "gen-badjson@example.com", tmp_path)
    fake_client = _FakeGeminiClient(responses=["not valid json", json.dumps(SAMPLE_CONTENT)])
    service = DocumentGenerationService(db_session, gemini_client=fake_client, sleep=lambda _: None)

    document = await service.generate(task.id, user.id)

    assert document.generation_status == "completed"
    assert len(fake_client.calls) == 2


async def test_generate_rejects_response_missing_required_chapters(db_session, tmp_path):
    user, task = await _make_task_with_upload(db_session, "gen-missing-ch@example.com", tmp_path)
    incomplete = {k: v for k, v in SAMPLE_CONTENT.items() if k != "chapter7"}
    fake_client = _FakeGeminiClient(responses=[json.dumps(incomplete)] * 3)
    service = DocumentGenerationService(db_session, gemini_client=fake_client, sleep=lambda _: None)

    with pytest.raises(DocumentGenerationError):
        await service.generate(task.id, user.id)

    assert len(fake_client.calls) == 3


async def test_generate_regenerates_existing_document_without_duplicate_row(db_session, tmp_path):
    user, task = await _make_task_with_upload(db_session, "gen-regen@example.com", tmp_path)
    service = DocumentGenerationService(
        db_session, gemini_client=_FakeGeminiClient(), sleep=lambda _: None
    )
    first = await service.generate(task.id, user.id)

    updated_content = {**SAMPLE_CONTENT, "chapter1": {"title": "Updated", "summary": "Updated summary."}}
    service2 = DocumentGenerationService(
        db_session,
        gemini_client=_FakeGeminiClient(responses=[json.dumps(updated_content)]),
        sleep=lambda _: None,
    )
    second = await service2.generate(task.id, user.id)

    assert first.id == second.id
    assert second.content["chapter1"]["title"] == "Updated"


async def _get_document(db_session, task_id):
    from sqlalchemy import select

    result = await db_session.execute(select(LearningDocument).where(LearningDocument.task_id == task_id))
    return result.scalar_one()
