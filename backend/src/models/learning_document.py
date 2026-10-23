"""LearningDocument SQLAlchemy model.

Columns MUST stay in sync with the `learning_documents` table defined in
backend/alembic/versions/001_initial_schema.py (T009) / data-model.md —
this is an ORM mapping of that existing schema, not a new source of truth.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import TIMESTAMP, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.task import Task


class LearningDocument(Base):
    __tablename__ = "learning_documents"

    # server_default must match the migration (001_initial_schema.py) so
    # SQLAlchemy knows the DB generates this value (via RETURNING) instead
    # of expecting the ORM to supply it.
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    # One-to-one with Task: unique=True enforces at most one LearningDocument
    # row per task (matches the migration's `unique=True` on task_id).
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    content: Mapped[dict[str, Any]] = mapped_column(JSONB(astext_type=Text()), nullable=False)
    generation_status: Mapped[str | None] = mapped_column(
        String(20), nullable=True, server_default="pending"
    )
    generation_started_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    generation_completed_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    generation_error: Mapped[str | None] = mapped_column(Text(), nullable=True)
    celery_task_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True, server_default=text("CURRENT_TIMESTAMP")
    )

    task: Mapped["Task"] = relationship(back_populates="learning_document")

    def __repr__(self) -> str:
        return f"LearningDocument(id={self.id!r}, task_id={self.task_id!r})"
