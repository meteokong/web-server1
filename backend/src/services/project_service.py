"""ProjectService: create, get, update, and soft-delete Projects.

Every lookup by project_id (get/update/soft_delete) requires the
requesting user_id and verifies ownership — a project that exists but
belongs to someone else raises the same NotFoundError as a project that
doesn't exist at all, so a caller can't use the error to probe for
other users' project ids (same reasoning as UserService's login error).
"""

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.exceptions import NotFoundError, ValidationAppError
from src.models.project import Project

_TRASH_RETENTION = timedelta(days=30)


class ProjectService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self, user_id: uuid.UUID, title: str, description: str | None = None
    ) -> Project:
        """Create a new project owned by ``user_id``. Raises ValidationAppError
        if the title is blank."""
        _validate_title(title)

        project = Project(user_id=user_id, title=title.strip(), description=description)
        self.db.add(project)
        await self.db.flush()
        return project

    async def get(self, project_id: uuid.UUID, user_id: uuid.UUID) -> Project:
        """Fetch a project owned by ``user_id``. Raises NotFoundError if it
        doesn't exist or isn't owned by ``user_id``."""
        return await self._get_owned_or_404(project_id, user_id)

    async def get_user_projects(self, user_id: uuid.UUID) -> list[Project]:
        """List a user's active (non-trashed) projects, newest first."""
        result = await self.db.execute(
            select(Project)
            .where(Project.user_id == user_id, Project.deletion_status == "active")
            .order_by(Project.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(
        self,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
        *,
        title: str | None = None,
        description: str | None = None,
    ) -> Project:
        """Update a project's title and/or description. Raises NotFoundError
        if the project doesn't exist or isn't owned by ``user_id``, or
        ValidationAppError if a given title is blank."""
        project = await self._get_owned_or_404(project_id, user_id)

        if title is not None:
            _validate_title(title)
            project.title = title.strip()
        if description is not None:
            project.description = description

        project.updated_at = datetime.now(UTC)
        await self.db.flush()
        return project

    async def soft_delete(self, project_id: uuid.UUID, user_id: uuid.UUID) -> Project:
        """Move a project to trash. Raises NotFoundError if it doesn't exist
        or isn't owned by ``user_id``."""
        project = await self._get_owned_or_404(project_id, user_id)

        now = datetime.now(UTC)
        project.deletion_status = "trashed"
        project.trashed_at = now
        project.scheduled_deletion_at = now + _TRASH_RETENTION
        await self.db.flush()
        return project

    async def _get_owned_or_404(self, project_id: uuid.UUID, user_id: uuid.UUID) -> Project:
        project = await self.db.get(Project, project_id)
        if project is None or project.user_id != user_id:
            raise NotFoundError("project not found")
        return project


def _validate_title(title: str) -> None:
    if not title.strip():
        raise ValidationAppError("title must not be blank")
