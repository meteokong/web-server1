"""RefreshToken SQLAlchemy model.

Columns MUST stay in sync with the `refresh_tokens` table defined in
backend/alembic/versions/001_initial_schema.py (T009) / data-model.md —
this is an ORM mapping of that existing schema, not a new source of truth.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import TIMESTAMP, Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.user import User


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    # SHA-256 hash of the refresh token — the raw token value is never stored.
    token_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    created_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    revoked: Mapped[bool | None] = mapped_column(Boolean(), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(back_populates="refresh_tokens")

    def __repr__(self) -> str:
        return f"RefreshToken(id={self.id!r}, user_id={self.user_id!r})"
