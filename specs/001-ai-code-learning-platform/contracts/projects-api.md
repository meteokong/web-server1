# Projects API Contract (T046–T050)

Base path: `/api/v1/projects` (mounted via `backend/src/api/router.py`).
All endpoints defined in `backend/src/api/projects.py`.

Backend building blocks already implemented and MUST be reused as-is:
- `ProjectService` (`backend/src/services/project_service.py`): `create(user_id, title, description=None)`, `get(project_id, user_id)`, `get_user_projects(user_id)`, `update(project_id, user_id, *, title=None, description=None)`, `soft_delete(project_id, user_id)`.
  - `get`/`update`/`soft_delete` all raise `NotFoundError` (404) when the project doesn't exist OR isn't owned by `user_id` (same error either way — don't leak existence of other users' projects).
  - `create`/`update` raise `ValidationAppError` (400) for a blank title.
- `get_current_user` dependency (`backend/src/api/dependencies.py`) — every endpoint below is protected.
- Error schema from `backend/src/api/exceptions.py`: `{"error": {"code", "message", "details"}}`.

## ProjectResponse shape

```json
{
  "id": "uuid-string",
  "user_id": "uuid-string",
  "title": "React 학습",
  "description": "optional text or null",
  "created_at": "2026-10-21T06:00:00+00:00",
  "updated_at": "2026-10-21T06:00:00+00:00",
  "last_activity_at": "2026-10-21T06:00:00+00:00",
  "deletion_status": "active",
  "trashed_at": null,
  "scheduled_deletion_at": null
}
```

## Endpoints

### `GET /api/v1/projects` (T046)
- Protected. Calls `ProjectService.get_user_projects(current_user.id)`.
- Success: `200 OK`, body = `{"projects": [ProjectResponse, ...]}` (active projects only, newest first).

### `POST /api/v1/projects` (T047)
- Protected. Request body: `{"title": "...", "description": "..." | null}`.
- Calls `ProjectService.create(current_user.id, title, description)`.
- Success: `201 Created`, body = ProjectResponse.
- Failure: `ValidationAppError` (blank title) → 400.

### `GET /api/v1/projects/{project_id}` (T048)
- Protected. Calls `ProjectService.get(project_id, current_user.id)`.
- Success: `200 OK`, body = ProjectResponse.
- Failure: `NotFoundError` (doesn't exist or not owned) → 404.

### `PATCH /api/v1/projects/{project_id}` (T049)
- Protected. Request body: `{"title": "..." | omitted, "description": "..." | null | omitted}` (partial update — only provided fields change).
- Calls `ProjectService.update(project_id, current_user.id, title=..., description=...)`.
- Success: `200 OK`, body = ProjectResponse.
- Failure: `NotFoundError` → 404, `ValidationAppError` (blank title) → 400.

### `DELETE /api/v1/projects/{project_id}` (T050)
- Protected. Calls `ProjectService.soft_delete(project_id, current_user.id)`.
- Success: `200 OK`, body = ProjectResponse (now with `deletion_status: "trashed"`, `trashed_at`, `scheduled_deletion_at` filled in). Project moves to trash, not permanently deleted (permanent deletion is Phase 10's `trash_service.py`).
- Failure: `NotFoundError` → 404.

## Frontend consumption (T051–T056)

`frontend/src/services/project-service.ts` wraps these via `apiClient` (see `auth-service.ts` for the pattern: thin async functions, snake_case response body mapped to a camelCase frontend type).

Suggested frontend `Project` type:

```ts
interface Project {
  id: string;
  title: string;
  description: string | null;
  createdAt: string;
  updatedAt: string;
  lastActivityAt: string;
  deletionStatus: "active" | "trashed";
}
```

`GET /projects` response is wrapped (`{"projects": [...]}`), not a bare array — unwrap it in `project-service.ts`.
