"""User SQLAlchemy model.

Columns MUST stay in sync with the `users` table defined in
backend/alembic/versions/001_initial_schema.py (T009) / data-model.md —
this is an ORM mapping of that existing schema, not a new source of truth.
"""

import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    skill_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    last_login_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, email={self.email!r})"
