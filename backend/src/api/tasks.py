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
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user
from src.db.session import get_db
from src.models.task import Task
from src.models.uploaded_code import UploadedCode
from src.models.user import User
from src.services.code_analysis.code_upload_service import CodeUploadService
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


class TaskUpdateRequest(BaseModel):
    title: str | None = None
    description: str | None = None


class CodeFileResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    file_name: str
    file_path: str | None
    file_extension: str | None
    file_size_bytes: int | None


class UploadedCodeResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    task_id: uuid.UUID
    detected_language: str | None
    complexity_level: str | None
    total_lines: int | None
    total_files: int | None
    upload_size_bytes: int | None
    code_files: list[CodeFileResponse]


def get_upload_root() -> Path | None:
    """FastAPI dependency so tests can override where CodeUploadService
    writes files (default: None, i.e. the configured storage/uploads)."""
    return None


@router.get("/projects/{project_id}/tasks", response_model=TaskListResponse)
async def list_tasks(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TaskListResponse:
    await ProjectService(db).get(project_id, current_user.id)
    tasks = await TaskService(db).list_by_project(project_id, current_user.id)
    return TaskListResponse(tasks=tasks)


@router.post(
    "/projects/{project_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    project_id: uuid.UUID,
    title: str = Form(...),
    description: str | None = Form(None),
    upload_method: str = Form(...),
    pasted_code: str | None = Form(None),
    files: list[UploadFile] = File(default=[]),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    upload_root: Path | None = Depends(get_upload_root),
) -> Task:
    task = await TaskService(db).create(
        project_id, current_user.id, title, description, upload_method
    )

    upload_entries = None
    if upload_method in ("file", "folder"):
        upload_entries = []
        for uploaded_file in files:
            full_path = uploaded_file.filename or ""
            file_name = Path(full_path).name
            relative_path = (
                full_path if upload_method == "folder" and full_path != file_name else None
            )
            upload_entries.append((file_name, relative_path, await uploaded_file.read()))

    await CodeUploadService(db, upload_root=upload_root).upload(
        task.id,
        current_user.id,
        upload_method,
        files=upload_entries,
        pasted_code=pasted_code,
    )
    return task


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Task:
    return await TaskService(db).get(task_id, current_user.id)


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: uuid.UUID,
    body: TaskUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Task:
    return await TaskService(db).update(
        task_id, current_user.id, title=body.title, description=body.description
    )


@router.delete("/tasks/{task_id}", response_model=TaskResponse)
async def delete_task(
    task_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Task:
    return await TaskService(db).soft_delete(task_id, current_user.id)


@router.get("/tasks/{task_id}/code", response_model=UploadedCodeResponse)
async def get_task_code(
    task_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UploadedCode:
    return await CodeUploadService(db).get_for_task(task_id, current_user.id)
