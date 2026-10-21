import axios, { type AxiosError } from "axios";

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

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiErrorBody>) => {
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
