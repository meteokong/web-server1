"""Integration tests for TaskService (T068) — run against the real database
(see tests/conftest.py's db_session fixture), mirroring
test_project_service.py's style.

A Task's "owner" is its parent Project's user_id (Task has no user_id of
its own), so every lookup goes through the project and raises the same
NotFoundError for "doesn't exist" and "exists but isn't yours" as
ProjectService.
"""

import uuid
from datetime import timedelta

import pytest

from src.api.exceptions import NotFoundError, ValidationAppError
from src.models.user import User
from src.services.project_service import ProjectService
from src.services.task_service import TaskService
from src.utils.security import hash_password


async def _make_user(db_session, email: str) -> User:
    user = User(email=email, password_hash=hash_password("correct-horse-123"))
    db_session.add(user)
    await db_session.flush()
    return user


async def _make_project(db_session, user: User, title: str = "Project"):
    return await ProjectService(db_session).create(user.id, title)


# ---------------------------------------------------------------------------
# create
# ---------------------------------------------------------------------------


async def test_create_persists_task_with_task_number_1_for_first_task(db_session):
    user = await _make_user(db_session, "create-ok@example.com")
    project = await _make_project(db_session, user)
    service = TaskService(db_session)

    task = await service.create(project.id, user.id, "My First Task", "learn loops", "paste")

    assert task.id is not None
    assert task.project_id == project.id
    assert task.task_number == 1
    assert task.title == "My First Task"
    assert task.description == "learn loops"
    assert task.upload_method == "paste"
    assert task.deletion_status == "active"


async def test_create_assigns_sequential_task_numbers_per_project(db_session):
    user = await _make_user(db_session, "create-seq@example.com")
    project = await _make_project(db_session, user)
    service = TaskService(db_session)

    first = await service.create(project.id, user.id, "Task One")
    second = await service.create(project.id, user.id, "Task Two")
    third = await service.create(project.id, user.id, "Task Three")

    assert [first.task_number, second.task_number, third.task_number] == [1, 2, 3]


async def test_create_task_numbers_are_independent_per_project(db_session):
    user = await _make_user(db_session, "create-independent@example.com")
    project_a = await _make_project(db_session, user, "Project A")
    project_b = await _make_project(db_session, user, "Project B")
    service = TaskService(db_session)

    task_a = await service.create(project_a.id, user.id, "Task In A")
    task_b = await service.create(project_b.id, user.id, "Task In B")

    assert task_a.task_number == 1
    assert task_b.task_number == 1


async def test_create_rejects_title_under_5_characters(db_session):
    user = await _make_user(db_session, "create-short@example.com")
    project = await _make_project(db_session, user)
    service = TaskService(db_session)

    with pytest.raises(ValidationAppError):
        await service.create(project.id, user.id, "abcd")


async def test_create_raises_not_found_for_unknown_project(db_session):
    user = await _make_user(db_session, "create-unknown@example.com")
    service = TaskService(db_session)

    with pytest.raises(NotFoundError):
        await service.create(uuid.uuid4(), user.id, "Valid Title")


async def test_create_raises_not_found_when_project_is_not_owned(db_session):
    owner = await _make_user(db_session, "create-owner@example.com")
    stranger = await _make_user(db_session, "create-stranger@example.com")
    project = await _make_project(db_session, owner)
    service = TaskService(db_session)

    with pytest.raises(NotFoundError):
        await service.create(project.id, stranger.id, "Valid Title")


# ---------------------------------------------------------------------------
# get
# ---------------------------------------------------------------------------


async def test_get_returns_the_task_for_its_owner(db_session):
    user = await _make_user(db_session, "get-ok@example.com")
    project = await _make_project(db_session, user)
    service = TaskService(db_session)
    created = await service.create(project.id, user.id, "Gettable Task")

    fetched = await service.get(created.id, user.id)

    assert fetched.id == created.id
    assert fetched.title == "Gettable Task"


async def test_get_raises_not_found_for_unknown_id(db_session):
    user = await _make_user(db_session, "get-unknown@example.com")
    service = TaskService(db_session)

    with pytest.raises(NotFoundError):
        await service.get(uuid.uuid4(), user.id)


async def test_get_raises_not_found_when_requested_by_a_non_owner(db_session):
    owner = await _make_user(db_session, "get-owner@example.com")
    stranger = await _make_user(db_session, "get-stranger@example.com")
    project = await _make_project(db_session, owner)
    service = TaskService(db_session)
    created = await service.create(project.id, owner.id, "Not Yours Task")

    with pytest.raises(NotFoundError):
        await service.get(created.id, stranger.id)


# ---------------------------------------------------------------------------
# list_by_project
# ---------------------------------------------------------------------------


async def test_list_by_project_returns_active_tasks_in_task_number_order(db_session):
    user = await _make_user(db_session, "list-ok@example.com")
    project = await _make_project(db_session, user)
    service = TaskService(db_session)
    first = await service.create(project.id, user.id, "Task One")
    second = await service.create(project.id, user.id, "Task Two")

    tasks = await service.list_by_project(project.id, user.id)

    assert [t.id for t in tasks] == [first.id, second.id]


async def test_list_by_project_excludes_trashed_tasks(db_session):
    user = await _make_user(db_session, "list-trash@example.com")
    project = await _make_project(db_session, user)
    service = TaskService(db_session)
    keep = await service.create(project.id, user.id, "Keep This Task")
    trashed = await service.create(project.id, user.id, "Trash This Task")
    await service.soft_delete(trashed.id, user.id)

    tasks = await service.list_by_project(project.id, user.id)

    assert [t.id for t in tasks] == [keep.id]


async def test_list_by_project_raises_not_found_for_non_owner(db_session):
    owner = await _make_user(db_session, "list-owner@example.com")
    stranger = await _make_user(db_session, "list-stranger@example.com")
    project = await _make_project(db_session, owner)
    service = TaskService(db_session)
    await service.create(project.id, owner.id, "Not Yours Task")

    with pytest.raises(NotFoundError):
        await service.list_by_project(project.id, stranger.id)


# ---------------------------------------------------------------------------
# update
# ---------------------------------------------------------------------------


async def test_update_changes_title_and_description(db_session):
    user = await _make_user(db_session, "update-ok@example.com")
    project = await _make_project(db_session, user)
    service = TaskService(db_session)
    created = await service.create(project.id, user.id, "Old Title", "old description")

    updated = await service.update(
        created.id, user.id, title="New Title", description="new description"
    )

    assert updated.title == "New Title"
    assert updated.description == "new description"


async def test_update_partial_keeps_other_field(db_session):
    user = await _make_user(db_session, "update-partial@example.com")
    project = await _make_project(db_session, user)
    service = TaskService(db_session)
    created = await service.create(project.id, user.id, "Keep Me", "keep description")

    updated = await service.update(created.id, user.id, description="updated only")

    assert updated.title == "Keep Me"
    assert updated.description == "updated only"


async def test_update_rejects_title_under_5_characters(db_session):
    user = await _make_user(db_session, "update-short@example.com")
    project = await _make_project(db_session, user)
    service = TaskService(db_session)
    created = await service.create(project.id, user.id, "Valid Title")

    with pytest.raises(ValidationAppError):
        await service.update(created.id, user.id, title="abcd")


async def test_update_raises_not_found_for_unknown_id(db_session):
    user = await _make_user(db_session, "update-unknown@example.com")
    service = TaskService(db_session)

    with pytest.raises(NotFoundError):
        await service.update(uuid.uuid4(), user.id, title="Whatever Title")


async def test_update_raises_not_found_when_requested_by_a_non_owner(db_session):
    owner = await _make_user(db_session, "update-owner@example.com")
    stranger = await _make_user(db_session, "update-stranger@example.com")
    project = await _make_project(db_session, owner)
    service = TaskService(db_session)
    created = await service.create(project.id, owner.id, "Not Yours Task")

    with pytest.raises(NotFoundError):
        await service.update(created.id, stranger.id, title="Hijacked Title")


# ---------------------------------------------------------------------------
# soft_delete
# ---------------------------------------------------------------------------


async def test_soft_delete_sets_trashed_status_and_schedule(db_session):
    user = await _make_user(db_session, "delete-ok@example.com")
    project = await _make_project(db_session, user)
    service = TaskService(db_session)
    created = await service.create(project.id, user.id, "Deletable Task")

    deleted = await service.soft_delete(created.id, user.id)

    assert deleted.deletion_status == "trashed"
    assert deleted.trashed_at is not None
    assert deleted.scheduled_deletion_at is not None
    assert deleted.scheduled_deletion_at - deleted.trashed_at == timedelta(days=30)


async def test_soft_delete_raises_not_found_for_unknown_id(db_session):
    user = await _make_user(db_session, "delete-unknown@example.com")
    service = TaskService(db_session)

    with pytest.raises(NotFoundError):
        await service.soft_delete(uuid.uuid4(), user.id)


async def test_soft_delete_raises_not_found_when_requested_by_a_non_owner(db_session):
    owner = await _make_user(db_session, "delete-owner@example.com")
    stranger = await _make_user(db_session, "delete-stranger@example.com")
    project = await _make_project(db_session, owner)
    service = TaskService(db_session)
    created = await service.create(project.id, owner.id, "Not Yours Task")

    with pytest.raises(NotFoundError):
        await service.soft_delete(created.id, stranger.id)
