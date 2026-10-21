"""Projects API endpoints (T046-T050): list, create, get, patch, delete.

Route handlers are intentionally thin — they delegate to ProjectService
(the actual business logic) and let the global exception handlers in
src/api/exceptions.py turn any AppError subclass it raises (NotFoundError,
ValidationAppError) into the standard {"error": {...}} JSON response. See
specs/001-ai-code-learning-platform/contracts/projects-api.md for the
full contract (request/response shapes, status codes).
"""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user
from src.db.session import get_db
from src.models.project import Project
from src.models.user import User
from src.services.project_service import ProjectService

router = APIRouter()


class ProjectResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    description: str | None
    created_at: datetime | None
    updated_at: datetime | None
    last_activity_at: datetime | None
    deletion_status: str | None
    trashed_at: datetime | None
    scheduled_deletion_at: datetime | None


class ProjectListResponse(BaseModel):
    projects: list[ProjectResponse]


class ProjectCreateRequest(BaseModel):
    title: str
    description: str | None = None


class ProjectUpdateRequest(BaseModel):
    title: str | None = None
    description: str | None = None


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectListResponse:
    projects = await ProjectService(db).get_user_projects(current_user.id)
    return ProjectListResponse(projects=projects)


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    body: ProjectCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Project:
    return await ProjectService(db).create(current_user.id, body.title, body.description)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Project:
    return await ProjectService(db).get(project_id, current_user.id)


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: uuid.UUID,
    body: ProjectUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Project:
    return await ProjectService(db).update(
        project_id, current_user.id, title=body.title, description=body.description
    )


@router.delete("/{project_id}", response_model=ProjectResponse)
async def delete_project(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Project:
    return await ProjectService(db).soft_delete(project_id, current_user.id)
