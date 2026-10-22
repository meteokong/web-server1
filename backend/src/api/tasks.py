"""Tasks API endpoints (T070-T075): list/create tasks under a project, and
get/patch/delete/code for a single task.

Route handlers are thin — they delegate to TaskService/CodeUploadService
and let the global exception handlers in src/api/exceptions.py turn any
AppError subclass into the standard {"error": {...}} JSON response (see
src/api/projects.py for the same pattern).

No fixed router prefix: task routes mix two path shapes
(/projects/{project_id}/tasks and /tasks/{task_id}), so each route spells
out its own full path and src/api/router.py includes this router with no
prefix (api_router itself already has prefix="/api/v1").
"""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user
from src.db.session import get_db
from src.models.user import User
from src.services.project_service import ProjectService
from src.services.task_service import TaskService

router = APIRouter()


class TaskResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    project_id: uuid.UUID
    task_number: int
    title: str
    description: str | None
    upload_method: str | None
    created_at: datetime | None
    updated_at: datetime | None
    deletion_status: str | None
    trashed_at: datetime | None
    scheduled_deletion_at: datetime | None


class TaskListResponse(BaseModel):
    tasks: list[TaskResponse]


@router.get("/projects/{project_id}/tasks", response_model=TaskListResponse)
async def list_tasks(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TaskListResponse:
    await ProjectService(db).get(project_id, current_user.id)
    tasks = await TaskService(db).list_by_project(project_id, current_user.id)
    return TaskListResponse(tasks=tasks)
