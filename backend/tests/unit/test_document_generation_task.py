"""Unit tests for the T094 Celery task wrapper
(src/tasks/document_generation.py). No real DB/Celery broker involved:

- Registration is checked directly against the celery_app instance
  (importing the module is enough to register the task; see celery_app.py's
  ``include`` list).
- The sync wrapper's only job is "call the async core function via
  asyncio.run()" — verified by monkeypatching that core function.

The actual generation logic (calling DocumentGenerationService) is covered
by the integration test in tests/integration/test_document_generation_task.py,
against a real DB.
"""

import src.tasks.document_generation as document_generation_task
from src.tasks.celery_app import celery_app
from src.tasks.document_generation import generate_document_task


def test_generate_document_task_is_registered_with_celery_app():
    assert "src.tasks.document_generation.generate_document_task" in celery_app.tasks


def test_generate_document_task_does_not_auto_retry_at_celery_level():
    # DocumentGenerationService already retries internally (T093, up to 3
    # attempts with exponential backoff) and leaves the LearningDocument
    # row in a terminal state either way, so Celery must not pile on
    # another layer of retries on top of that.
    assert generate_document_task.max_retries == 0


def test_generate_document_task_calls_async_core_via_asyncio_run(monkeypatch):
    calls = []

    async def fake_generate_document(task_id, user_id, *, gemini_client=None):
        calls.append((task_id, user_id, gemini_client))

    monkeypatch.setattr(document_generation_task, "_generate_document", fake_generate_document)

    generate_document_task("11111111-1111-1111-1111-111111111111", "22222222-2222-2222-2222-222222222222")

    assert calls == [
        (
            "11111111-1111-1111-1111-111111111111",
            "22222222-2222-2222-2222-222222222222",
            None,
        )
    ]
