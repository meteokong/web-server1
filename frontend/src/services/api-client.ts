import axios, { type AxiosError, type InternalAxiosRequestConfig } from "axios";
import { useAuthStore } from "../stores/auth-store";

/**
 * Shared axios instance every service module (auth-service, project-service,
 * ...) builds its requests on top of.
 */
export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1",
  // Access/refresh tokens live in HTTPOnly cookies (research.md auth
  // design), so every request must send them — the browser can't be
  // asked to attach them manually like a header.
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

/** Matches the error schema every backend error response uses (src/api/exceptions.py, T016). */
export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
    details?: unknown;
  };
}

/** Thrown by the response interceptor below for any failed request. */
export class ApiError extends Error {
  readonly status: number | undefined;
  readonly code: string;
  readonly details: unknown;

  constructor(status: number | undefined, code: string, message: string, details?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

type RetriableRequestConfig = InternalAxiosRequestConfig & { _retriedAfterRefresh?: boolean };

/**
 * T038 auto-refresh design: the access token lives in an HTTPOnly cookie
 * we can't read from JS, so we can't check its `exp` up front — the
 * only signal we get is a 401 on whatever request happened to use it.
 * So: on any 401 (that isn't the refresh call itself, and hasn't
 * already been retried once), attempt exactly one POST /auth/refresh,
 * then retry the original request once. If the refresh call also
 * fails, the user's session is truly gone — clear the auth store so
 * ProtectedRoute (T037) redirects to /login on the next render.
 *
 * `inFlightRefresh` dedupes concurrent 401s (e.g. several queries firing
 * at once right as the access token expires) into a single refresh
 * call instead of one per failed request.
 */
let inFlightRefresh: Promise<void> | null = null;

function isRefreshRequest(config?: InternalAxiosRequestConfig): boolean {
  return Boolean(config?.url?.includes("/auth/refresh"));
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<ApiErrorBody>) => {
    const originalRequest = error.config as RetriableRequestConfig | undefined;

    if (
      error.response?.status === 401 &&
      originalRequest &&
      !originalRequest._retriedAfterRefresh &&
      !isRefreshRequest(originalRequest)
    ) {
      originalRequest._retriedAfterRefresh = true;
      try {
        inFlightRefresh ??= apiClient
          .post("/auth/refresh")
          .then(() => undefined)
          .finally(() => {
            inFlightRefresh = null;
          });
        await inFlightRefresh;
        return apiClient(originalRequest);
      } catch {
        // Refresh failed too: the session can't be recovered. Clear the
        // client-side auth state and fall through to the normal error
        // conversion below (auth-store has no dependency back on
        // api-client, so this static import doesn't create a cycle).
        useAuthStore.getState().clearUser();
      }
    }

    const body = error.response?.data;
    if (body?.error) {
      return Promise.reject(
        new ApiError(
          error.response?.status,
          body.error.code,
          body.error.message,
          body.error.details,
        ),
      );
    }
    // Network error, timeout, or a response that doesn't match our
    // backend's error schema (shouldn't happen, but don't assume it won't).
    return Promise.reject(new ApiError(error.response?.status, "network_error", error.message));
  },
);
