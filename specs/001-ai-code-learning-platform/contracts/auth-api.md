# Auth API Contract (T028–T031)

Base path: `/api/v1/auth` (mounted via `backend/src/api/router.py`, T015).
All endpoints defined in `backend/src/api/auth.py`.

Backend building blocks already implemented and MUST be reused as-is
(do not reimplement their logic in the route handlers):
- `UserService` (`backend/src/services/auth/user_service.py`): `register(email, password)`, `login(email, password)`, `logout(user_id)`
- `TokenService` (`backend/src/services/auth/token_service.py`): `issue_tokens(user)`, `verify_access_token(token)`, `rotate_refresh_token(token)`
- `get_current_user` dependency (`backend/src/api/dependencies.py`)
- Error schema from `backend/src/api/exceptions.py`: `{"error": {"code", "message", "details"}}` — services already raise `ConflictError`/`UnauthorizedError`/`ValidationAppError`, so route handlers mostly just call the service and let the global exception handlers do the rest.

## Cookies

Both tokens are set as **HTTPOnly cookies**, never returned in a JSON body:

| Cookie name | Set by | Max-Age | Notes |
|---|---|---|---|
| `access_token` | login, refresh | 15 min (`JWTSettings.access_token_expire_minutes`) | `httponly=True`, `samesite="strict"`, `secure=` (True unless `ENVIRONMENT=development`) |
| `refresh_token` | login, refresh | 7 days (`JWTSettings.refresh_token_expire_days`) | same flags as above |

Logout clears both cookies (`response.delete_cookie(...)`).

## UserResponse shape

Every endpoint that returns a user returns this shape (never `password_hash`):

```json
{
  "id": "uuid-string",
  "email": "user@example.com",
  "skill_level": "Complete Beginner",
  "created_at": "2026-10-21T06:00:00+00:00"
}
```

## Endpoints

### `POST /api/v1/auth/register` (T028)

Request body: `{"email": "...", "password": "..."}`

- Calls `UserService.register(email, password)`.
- Success: `201 Created`, body = UserResponse. **Does not log the user in** (no cookies set) — register and login are separate steps.
- Failure: service raises `ValidationAppError` (weak password) → 400, or `ConflictError` (duplicate email) → 409. Let the global handler format it.

### `POST /api/v1/auth/login` (T029)

Request body: `{"email": "...", "password": "..."}`

- Calls `UserService.login(email, password)`, then on success `TokenService.issue_tokens(user)`.
- Success: `200 OK`, body = UserResponse, sets `access_token` + `refresh_token` cookies.
- Failure: `UnauthorizedError` (wrong email/password, same message for both) → 401.

### `GET /api/v1/auth/me` (T029A)

- Protected: `Depends(get_current_user)`.
- Success: `200 OK`, body = UserResponse for the current user.
- Failure: `UnauthorizedError` (no/invalid/expired cookie) → 401 (handled entirely by the dependency, nothing extra to do in the route).

### `POST /api/v1/auth/logout` (T030)

- Protected: `Depends(get_current_user)`.
- Calls `UserService.logout(user.id)` (revokes **all** of the user's refresh tokens — every session, not just this one).
- Success: `200 OK`, body `{"message": "logged out"}`, clears both cookies.

### `POST /api/v1/auth/refresh` (T031)

- Reads the `refresh_token` cookie directly (NOT behind `get_current_user`, since the access token may already be expired — that's the whole point of this endpoint).
- If the cookie is missing: `401` with the same `UnauthorizedError` shape as an invalid token (don't special-case "missing" vs "invalid" here either).
- Calls `TokenService.rotate_refresh_token(refresh_token)` → on success, sets the **new** `access_token` + `refresh_token` cookies (rotation — the old refresh token is now revoked, per T026).
- Success: `200 OK`, body = UserResponse for the token's subject (look the user up by `payload["sub"]` the same way `get_current_user` does, or have `rotate_refresh_token` surface it — route handler's choice).
- Failure: `UnauthorizedError` → 401, and the route should clear both cookies in the response (the client's refresh token is dead either way).

## Testing pattern (MANDATORY — see docs/task-reports/TASK-027-*.md)

Use `httpx.AsyncClient` + `httpx.ASGITransport` against the real app and
a real DB session fixture (`tests/conftest.py`'s `db_session`), exactly
like `backend/tests/integration/test_dependencies.py`. **Do NOT use
`fastapi.testclient.TestClient`** — it runs the ASGI app on a separate
thread/event loop, which breaks asyncpg connections tied to the test's
own loop (see that Task Report for the full story).
