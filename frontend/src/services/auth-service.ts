import { apiClient } from "./api-client";
import { useAuthStore, type AuthUser } from "../stores/auth-store";

/** Shape returned by every auth endpoint that returns a user (auth-api.md). */
interface UserResponseBody {
  id: string;
  email: string;
  skill_level: string;
  created_at: string;
}

function toAuthUser(body: UserResponseBody): AuthUser {
  return { id: body.id, email: body.email, skillLevel: body.skill_level };
}

/**
 * POST /auth/register. Per the contract this does NOT log the user in
 * (no cookies are set by this endpoint) — register and login are
 * deliberately separate steps, so this does not touch useAuthStore.
 */
export async function register(email: string, password: string): Promise<AuthUser> {
  const response = await apiClient.post<UserResponseBody>("/auth/register", {
    email,
    password,
  });
  return toAuthUser(response.data);
}

/**
 * POST /auth/login. On success the backend sets the access/refresh
 * HTTPOnly cookies and returns the user, which we push into
 * useAuthStore so the rest of the app (ProtectedRoute, nav, etc.)
 * immediately knows "who is logged in".
 */
export async function login(email: string, password: string): Promise<AuthUser> {
  const response = await apiClient.post<UserResponseBody>("/auth/login", {
    email,
    password,
  });
  const user = toAuthUser(response.data);
  useAuthStore.getState().setUser(user);
  return user;
}

/**
 * POST /auth/logout. Clears the server-side cookies; we mirror that by
 * clearing the client-side auth store regardless of what the backend
 * returns, so the UI always reflects "logged out" once this resolves.
 */
export async function logout(): Promise<void> {
  await apiClient.post("/auth/logout");
  useAuthStore.getState().clearUser();
}

/**
 * GET /auth/me. Used by useAuth (T038) on app mount to discover "is
 * there already a valid session cookie?" — does not touch the store
 * itself, that's the caller's job (mirrors register()'s split between
 * "make the API call" and "decide what it means for the store").
 */
export async function getCurrentUser(): Promise<AuthUser> {
  const response = await apiClient.get<UserResponseBody>("/auth/me");
  return toAuthUser(response.data);
}
