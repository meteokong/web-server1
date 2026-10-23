import { beforeEach, describe, expect, it, vi } from "vitest";
import { apiClient } from "./api-client";
import { useAuthStore } from "../stores/auth-store";
import { login, logout, register } from "./auth-service";

vi.mock("./api-client", () => ({
  apiClient: {
    post: vi.fn(),
  },
}));

const mockedPost = apiClient.post as unknown as ReturnType<typeof vi.fn>;

const userResponseBody = {
  id: "user-1",
  email: "test@example.com",
  skill_level: "Complete Beginner",
  created_at: "2026-10-21T06:00:00+00:00",
};

describe("auth-service", () => {
  beforeEach(() => {
    mockedPost.mockReset();
    useAuthStore.setState({ user: null, isAuthenticated: false, isInitializing: true });
  });

  describe("register", () => {
    it("POSTs to /auth/register and returns the created user without logging in", async () => {
      mockedPost.mockResolvedValue({ data: userResponseBody });

      const user = await register("test@example.com", "Sup3rSecret!");

      expect(mockedPost).toHaveBeenCalledWith("/auth/register", {
        email: "test@example.com",
        password: "Sup3rSecret!",
      });
      expect(user).toEqual({
        id: "user-1",
        email: "test@example.com",
        skillLevel: "Complete Beginner",
      });
      // register must NOT log the user in (contract: "Does not log the user in")
      expect(useAuthStore.getState().isAuthenticated).toBe(false);
    });
  });

  describe("login", () => {
    it("POSTs to /auth/login and updates the auth store with the logged-in user", async () => {
      mockedPost.mockResolvedValue({ data: userResponseBody });

      const user = await login("test@example.com", "Sup3rSecret!");

      expect(mockedPost).toHaveBeenCalledWith("/auth/login", {
        email: "test@example.com",
        password: "Sup3rSecret!",
      });
      expect(user).toEqual({
        id: "user-1",
        email: "test@example.com",
        skillLevel: "Complete Beginner",
      });
      expect(useAuthStore.getState().user).toEqual(user);
      expect(useAuthStore.getState().isAuthenticated).toBe(true);
    });

    it("propagates a rejected login without touching the auth store", async () => {
      const error = new Error("이메일 또는 비밀번호가 올바르지 않습니다.");
      mockedPost.mockRejectedValue(error);

      await expect(login("test@example.com", "wrong")).rejects.toThrow(error.message);
      expect(useAuthStore.getState().isAuthenticated).toBe(false);
    });
  });

  describe("logout", () => {
    it("POSTs to /auth/logout and clears the auth store", async () => {
      useAuthStore.getState().setUser({
        id: "user-1",
        email: "test@example.com",
        skillLevel: "Complete Beginner",
      });
      mockedPost.mockResolvedValue({ data: { message: "logged out" } });

      await logout();

      expect(mockedPost).toHaveBeenCalledWith("/auth/logout");
      expect(useAuthStore.getState().user).toBeNull();
      expect(useAuthStore.getState().isAuthenticated).toBe(false);
    });
  });
});
