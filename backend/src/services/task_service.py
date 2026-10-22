"""TaskService: create, get, list, update, and soft-delete Tasks.

A Task has no user_id of its own — its owner is its parent Project's
user_id — so every lookup joins through Project and raises the same
NotFoundError for "doesn't exist" as for "exists but isn't yours" (same
anti-enumeration reasoning as ProjectService).
"""

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.exceptions import NotFoundError, ValidationAppError

# Task.uploaded_code / UploadedCode.code_files are declared as string-named
# relationships (see src/models/task.py's TYPE_CHECKING-only imports, which
# avoid a circular import at module load time). SQLAlchemy only resolves
# those names when it configures all mappers, which happens the first time
# any one of them is queried — so both classes must have been imported
# *somewhere* by then, or Task's own mapper configuration fails with
# InvalidRequestError. This module is the first to actually query Task.
from src.models.code_file import CodeFile  # noqa: F401
from src.models.project import Project
from src.models.task import Task
from src.models.uploaded_code import UploadedCode  # noqa: F401

_TRASH_RETENTION = timedelta(days=30)
_TITLE_MIN_LENGTH = 5  # data-model.md: tasks.title_min_length CHECK (char_length(title) >= 5)


class TaskService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
        title: str,
        description: str | None = None,
        upload_method: str | None = None,
    ) -> Task:
        """Create a new task under ``project_id``, owned (via the project)
        by ``user_id``. Raises NotFoundError if the project doesn't exist
        or isn't owned by ``user_id``, or ValidationAppError if the title
        is under 5 characters."""
        await self._get_owned_project_or_404(project_id, user_id)
        _validate_title(title)

        task_number = await self._next_task_number(project_id)
        task = Task(
            project_id=project_id,
            task_number=task_number,
            title=title.strip(),
            description=description,
            upload_method=upload_method,
        )
        self.db.add(task)
        await self.db.flush()
        return task

    async def get(self, task_id: uuid.UUID, user_id: uuid.UUID) -> Task:
        """Fetch a task owned (via its project) by ``user_id``. Raises
        NotFoundError if it doesn't exist or isn't owned by ``user_id``."""
        return await self._get_owned_or_404(task_id, user_id)

    async def list_by_project(self, project_id: uuid.UUID, user_id: uuid.UUID) -> list[Task]:
        """List a project's active (non-trashed) tasks, in task_number
        order. Raises NotFoundError if the project doesn't exist or isn't
        owned by ``user_id``."""
        await self._get_owned_project_or_404(project_id, user_id)
        result = await self.db.execute(
            select(Task)
            .where(Task.project_id == project_id, Task.deletion_status == "active")
            .order_by(Task.task_number.asc())
        )
        return list(result.scalars().all())

    async def update(
        self,
        task_id: uuid.UUID,
        user_id: uuid.UUID,
        *,
        title: str | None = None,
        description: str | None = None,
    ) -> Task:
        """Update a task's title and/or description. Raises NotFoundError
        if the task doesn't exist or isn't owned by ``user_id``, or
        ValidationAppError if a given title is under 5 characters."""
        task = await self._get_owned_or_404(task_id, user_id)

        if title is not None:
            _validate_title(title)
            task.title = title.strip()
        if description is not None:
            task.description = description

        task.updated_at = datetime.now(UTC)
        await self.db.flush()
        return task

    async def soft_delete(self, task_id: uuid.UUID, user_id: uuid.UUID) -> Task:
        """Move a task to trash. Raises NotFoundError if it doesn't exist
        or isn't owned by ``user_id``."""
        task = await self._get_owned_or_404(task_id, user_id)

        now = datetime.now(UTC)
        task.deletion_status = "trashed"
        task.trashed_at = now
        task.scheduled_deletion_at = now + _TRASH_RETENTION
        await self.db.flush()
        return task

    async def _get_owned_or_404(self, task_id: uuid.UUID, user_id: uuid.UUID) -> Task:
        task = await self.db.get(Task, task_id)
        if task is None:
            raise NotFoundError("task not found")
        await self._get_owned_project_or_404(task.project_id, user_id)
        return task

    async def _get_owned_project_or_404(self, project_id: uuid.UUID, user_id: uuid.UUID) -> Project:
        project = await self.db.get(Project, project_id)
        if project is None or project.user_id != user_id:
            raise NotFoundError("project not found")
        return project

    async def _next_task_number(self, project_id: uuid.UUID) -> int:
        result = await self.db.execute(
            select(func.max(Task.task_number)).where(Task.project_id == project_id)
        )
        current_max = result.scalar()
        return (current_max or 0) + 1


def _validate_title(title: str) -> None:
    if len(title.strip()) < _TITLE_MIN_LENGTH:
        raise ValidationAppError(f"title must be at least {_TITLE_MIN_LENGTH} characters")
