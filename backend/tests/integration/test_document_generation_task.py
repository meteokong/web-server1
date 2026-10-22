"""Integration tests for the T094 Celery task's generation logic
(src/tasks/document_generation.py), run against the real database (see
tests/conftest.py's db_session fixture) — same reasoning as
tests/integration/test_document_generation_service.py: these behaviors
(LearningDocument persisting, DocumentGenerationError propagating) are
DB-level / orchestration guarantees, not something worth faking.

``_run_generation`` is the task's core logic factored out of the
Celery-specific "create my own engine/session, commit, dispose" wrapper
(``_generate_document``) precisely so it can be exercised directly
against this fixture's session instead of a second, independent DB
connection that wouldn't see this fixture's (uncommitted) rows.

Gemini itself is never called: a fake client is injected, matching
GeminiClient's ``generate_content`` signature (see
test_document_generation_service.py for the same fake).
"""

import json

import pytest

from src.models.learning_document import LearningDocument
from src.models.user import User
from src.services.ai.gemini_client import GeminiAPIError
from src.services.code_analysis.code_upload_service import CodeUploadService
from src.services.document.document_generation_service import DocumentGenerationError
from src.services.project_service import ProjectService
from src.services.task_service import TaskService
from src.tasks.document_generation import _run_generation
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
    def __init__(self, responses=None, fail_count=0):
        self._responses = list(responses) if responses is not None else [json.dumps(SAMPLE_CONTENT)]
        self._fail_count = fail_count
        self.calls = 0

    def generate_content(self, prompt, *, system_instruction=None, response_mime_type=None):
        self.calls += 1
        if self.calls <= self._fail_count:
            raise GeminiAPIError("transient failure", code=503)
        return self._responses.pop(0)


async def _make_task_with_upload(db_session, email: str, tmp_path):
    user = User(email=email, password_hash=hash_password("correct-horse-123"))
    db_session.add(user)
    await db_session.flush()
    project = await ProjectService(db_session).create(user.id, "Project")
    task = await TaskService(db_session).create(project.id, user.id, "A Task", upload_method="file")
    await CodeUploadService(db_session, upload_root=tmp_path).upload(
        task.id, user.id, "file", files=[("main.py", None, b"def add(a, b):\n    return a + b\n")]
    )
    return user, task


async def test_run_generation_completes_document_with_fake_gemini_client(db_session, tmp_path):
    user, task = await _make_task_with_upload(db_session, "task-gen-ok@example.com", tmp_path)
    fake_client = _FakeGeminiClient()

    await _run_generation(db_session, str(task.id), str(user.id), fake_client)

    from sqlalchemy import select

    result = await db_session.execute(
        select(LearningDocument).where(LearningDocument.task_id == task.id)
    )
    document = result.scalar_one()
    assert document.generation_status == "completed"
    assert document.content == SAMPLE_CONTENT


async def test_run_generation_propagates_error_without_swallowing_it(db_session, tmp_path):
    user, task = await _make_task_with_upload(db_session, "task-gen-fail@example.com", tmp_path)
    fake_client = _FakeGeminiClient(fail_count=10)

    with pytest.raises(DocumentGenerationError):
        await _run_generation(db_session, str(task.id), str(user.id), fake_client)
