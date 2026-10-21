"""Task SQLAlchemy model.

Columns MUST stay in sync with the `tasks` table defined in
backend/alembic/versions/001_initial_schema.py (T009) / data-model.md —
this is an ORM mapping of that existing schema, not a new source of truth.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import TIMESTAMP, ForeignKey, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.project import Project


class Task(Base):
    __tablename__ = "tasks"

    # server_default must match the migration (001_initial_schema.py) so
    # SQLAlchemy knows the DB generates this value (via RETURNING) instead
    # of expecting the ORM to supply it.
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    task_number: Mapped[int] = mapped_column(Integer(), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    upload_method: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True, server_default=text("CURRENT_TIMESTAMP")
    )
    deletion_status: Mapped[str | None] = mapped_column(
        String(20), nullable=True, server_default="active"
    )
    trashed_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    scheduled_deletion_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )

    project: Mapped["Project"] = relationship(back_populates="tasks")

    def __repr__(self) -> str:
        return f"Task(id={self.id!r}, project_id={self.project_id!r}, task_number={self.task_number!r})"
