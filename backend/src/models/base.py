"""Shared declarative base for all SQLAlchemy models.

A consistent naming convention is applied to constraints/indexes so that
Alembic autogenerate (used for schema changes after the initial migration)
produces stable, predictable names instead of SQLAlchemy's default
auto-generated ones.
"""

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Base class every ORM model (User, Project, Task, ...) inherits from."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)
