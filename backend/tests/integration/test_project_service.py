"""Integration tests for ProjectService — run against the real database
(see tests/conftest.py's db_session fixture) because the behaviors that
matter here (FK to users, soft-delete timestamps actually persisting)
are DB-level guarantees, not something a mocked session would prove.
"""

from datetime import timedelta

import pytest

from src.api.exceptions import NotFoundError, ValidationAppError
from src.models.user import User
from src.services.project_service import ProjectService
from src.utils.security import hash_password


async def _make_user(db_session, email: str) -> User:
    user = User(email=email, password_hash=hash_password("correct-horse-123"))
    db_session.add(user)
    await db_session.flush()
    return user


async def test_create_persists_project_owned_by_user(db_session):
    user = await _make_user(db_session, "create-ok@example.com")
    service = ProjectService(db_session)

    project = await service.create(user.id, "My First Project", "learning FastAPI")

    assert project.id is not None
    assert project.user_id == user.id
    assert project.title == "My First Project"
    assert project.description == "learning FastAPI"
    assert project.deletion_status == "active"


async def test_create_rejects_blank_title(db_session):
    user = await _make_user(db_session, "create-blank@example.com")
    service = ProjectService(db_session)

    with pytest.raises(ValidationAppError):
        await service.create(user.id, "   ")


async def test_get_returns_the_project_for_its_owner(db_session):
    user = await _make_user(db_session, "get-ok@example.com")
    service = ProjectService(db_session)
    created = await service.create(user.id, "Gettable Project")

    fetched = await service.get(created.id, user.id)

    assert fetched.id == created.id
    assert fetched.title == "Gettable Project"


async def test_get_raises_not_found_for_unknown_id(db_session):
    import uuid

    user = await _make_user(db_session, "get-unknown@example.com")
    service = ProjectService(db_session)
    with pytest.raises(NotFoundError):
        await service.get(uuid.uuid4(), user.id)


async def test_get_raises_not_found_when_requested_by_a_non_owner(db_session):
    owner = await _make_user(db_session, "get-owner@example.com")
    stranger = await _make_user(db_session, "get-stranger@example.com")
    service = ProjectService(db_session)
    created = await service.create(owner.id, "Not Yours")

    with pytest.raises(NotFoundError):
        await service.get(created.id, stranger.id)


async def test_update_changes_title_and_description(db_session):
    user = await _make_user(db_session, "update-ok@example.com")
    service = ProjectService(db_session)
    created = await service.create(user.id, "Old Title", "old description")

    updated = await service.update(
        created.id, user.id, title="New Title", description="new description"
    )

    assert updated.title == "New Title"
    assert updated.description == "new description"


async def test_update_rejects_blank_title(db_session):
    user = await _make_user(db_session, "update-blank@example.com")
    service = ProjectService(db_session)
    created = await service.create(user.id, "Valid Title")

    with pytest.raises(ValidationAppError):
        await service.update(created.id, user.id, title="   ")


async def test_update_raises_not_found_for_unknown_id(db_session):
    import uuid

    user = await _make_user(db_session, "update-unknown@example.com")
    service = ProjectService(db_session)
    with pytest.raises(NotFoundError):
        await service.update(uuid.uuid4(), user.id, title="whatever")


async def test_update_raises_not_found_when_requested_by_a_non_owner(db_session):
    owner = await _make_user(db_session, "update-owner@example.com")
    stranger = await _make_user(db_session, "update-stranger@example.com")
    service = ProjectService(db_session)
    created = await service.create(owner.id, "Not Yours")

    with pytest.raises(NotFoundError):
        await service.update(created.id, stranger.id, title="Hijacked")


async def test_soft_delete_sets_trashed_status_and_schedule(db_session):
    user = await _make_user(db_session, "delete-ok@example.com")
    service = ProjectService(db_session)
    created = await service.create(user.id, "Deletable Project")

    deleted = await service.soft_delete(created.id, user.id)

    assert deleted.deletion_status == "trashed"
    assert deleted.trashed_at is not None
    assert deleted.scheduled_deletion_at is not None
    assert deleted.scheduled_deletion_at - deleted.trashed_at == timedelta(days=30)


async def test_soft_delete_raises_not_found_for_unknown_id(db_session):
    import uuid

    user = await _make_user(db_session, "delete-unknown@example.com")
    service = ProjectService(db_session)
    with pytest.raises(NotFoundError):
        await service.soft_delete(uuid.uuid4(), user.id)


async def test_soft_delete_raises_not_found_when_requested_by_a_non_owner(db_session):
    owner = await _make_user(db_session, "delete-owner@example.com")
    stranger = await _make_user(db_session, "delete-stranger@example.com")
    service = ProjectService(db_session)
    created = await service.create(owner.id, "Not Yours")

    with pytest.raises(NotFoundError):
        await service.soft_delete(created.id, stranger.id)


async def test_get_user_projects_returns_only_this_users_active_projects(db_session):
    owner = await _make_user(db_session, "list-owner@example.com")
    other = await _make_user(db_session, "list-other@example.com")
    service = ProjectService(db_session)
    await service.create(owner.id, "React 학습")
    await service.create(owner.id, "Python 기초")
    await service.create(other.id, "Someone Else's Project")

    projects = await service.get_user_projects(owner.id)

    assert {p.title for p in projects} == {"React 학습", "Python 기초"}
    assert all(p.user_id == owner.id for p in projects)


async def test_get_user_projects_excludes_trashed_projects(db_session):
    owner = await _make_user(db_session, "list-trash@example.com")
    service = ProjectService(db_session)
    keep = await service.create(owner.id, "React 학습")
    trashed = await service.create(owner.id, "Python 기초")
    await service.soft_delete(trashed.id)

    projects = await service.get_user_projects(owner.id)

    assert [p.id for p in projects] == [keep.id]


async def test_get_user_projects_returns_empty_list_for_user_with_no_projects(db_session):
    owner = await _make_user(db_session, "list-empty@example.com")
    service = ProjectService(db_session)

    projects = await service.get_user_projects(owner.id)

    assert projects == []
