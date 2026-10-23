"""Documents API endpoints (T097/T098): read a Task's generated
LearningDocument and its generation status.

Route handlers are thin — they delegate to DocumentQueueService (T095)
and let the global exception handlers in src/api/exceptions.py turn any
AppError subclass into the standard {"error": {...}} JSON response (see
src/api/tasks.py for the same pattern).

No fixed router prefix: like tasks.py, every route here spells out its
own full /tasks/{task_id}/... path, so src/api/router.py includes this
router with no prefix.
"""

import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user
from src.db.session import get_db
from src.models.user import User
from src.services.document.document_queue_service import DocumentQueueService

router = APIRouter()


class DocumentStatusResponse(BaseModel):
    task_id: uuid.UUID
    generation_status: str | None
    generation_error: str | None
    generation_started_at: datetime | None
    generation_completed_at: datetime | None


class DocumentResponse(BaseModel):
    task_id: uuid.UUID
    generation_status: str | None
    generation_error: str | None
    content: dict[str, Any] | None


@router.get("/tasks/{task_id}/document/status", response_model=DocumentStatusResponse)
async def get_document_status(
    task_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentStatusResponse:
    status = await DocumentQueueService(db).get_status(task_id, current_user.id)
    return DocumentStatusResponse(**status)


@router.get("/tasks/{task_id}/document", response_model=DocumentResponse)
async def get_document(
    task_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentResponse:
    document = await DocumentQueueService(db).get_document(task_id, current_user.id)
    return DocumentResponse(**document)
