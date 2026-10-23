"""CodeFile SQLAlchemy model.

Columns MUST stay in sync with the `code_files` table defined in
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
    from src.models.uploaded_code import UploadedCode


class CodeFile(Base):
    __tablename__ = "code_files"

    # server_default must match the migration (001_initial_schema.py) so
    # SQLAlchemy knows the DB generates this value (via RETURNING) instead
    # of expecting the ORM to supply it.
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    uploaded_code_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("uploaded_code.id", ondelete="CASCADE"), nullable=False
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    # Relative path within a folder upload's structure (null for single-file uploads).
    file_path: Mapped[str | None] = mapped_column(Text(), nullable=True)
    file_extension: Mapped[str | None] = mapped_column(String(20), nullable=True)
    file_size_bytes: Mapped[int | None] = mapped_column(Integer(), nullable=True)
    # Actual path on the filesystem (storage/uploads/{user_id}/{task_id}/...), not user-facing.
    storage_path: Mapped[str] = mapped_column(Text(), nullable=False)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True, server_default=text("CURRENT_TIMESTAMP")
    )

    uploaded_code: Mapped["UploadedCode"] = relationship(back_populates="code_files")

    def __repr__(self) -> str:
        return f"CodeFile(id={self.id!r}, uploaded_code_id={self.uploaded_code_id!r}, file_name={self.file_name!r})"
