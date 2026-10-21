"""UploadedCode SQLAlchemy model.

Columns MUST stay in sync with the `uploaded_code` table defined in
backend/alembic/versions/001_initial_schema.py (T009) / data-model.md —
this is an ORM mapping of that existing schema, not a new source of truth.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import TIMESTAMP, ForeignKey, Integer, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.task import Task


class UploadedCode(Base):
    __tablename__ = "uploaded_code"

    # server_default must match the migration (001_initial_schema.py) so
    # SQLAlchemy knows the DB generates this value (via RETURNING) instead
    # of expecting the ORM to supply it.
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    # One-to-one with Task: unique=True enforces at most one UploadedCode
    # row per task (matches the migration's `unique=True` on task_id).
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    detected_language: Mapped[str | None] = mapped_column(String(50), nullable=True)
    complexity_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    total_lines: Mapped[int | None] = mapped_column(Integer(), nullable=True)
    total_files: Mapped[int | None] = mapped_column(Integer(), nullable=True)
    upload_size_bytes: Mapped[int | None] = mapped_column(Integer(), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True, server_default=text("CURRENT_TIMESTAMP")
    )

    task: Mapped["Task"] = relationship(back_populates="uploaded_code")

    def __repr__(self) -> str:
        return f"UploadedCode(id={self.id!r}, task_id={self.task_id!r})"
