import { create } from "zustand";

/**
 * Non-sensitive user identity, shown in the UI (e.g. "Hi, {email}").
 * The actual access/refresh JWTs never enter JS at all — they live in
 * HTTPOnly cookies the browser manages (research.md auth design) — so
 * this store only ever holds state derived from an API response, never
 * a token value.
 */
export interface AuthUser {
  id: string;
  email: string;
  skillLevel: string;
}

interface AuthState {
  user: AuthUser | null;
  isAuthenticated: boolean;
  /**
   * True until the app's first auth check (GET /auth/me, see T038's
   * useAuth hook) resolves. Lets ProtectedRoute (T037) wait for that
   * answer instead of redirecting to /login before it's known.
   */
  isInitializing: boolean;
  setUser: (user: AuthUser) => void;
  clearUser: () => void;
  finishInitializing: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isInitializing: true,
  setUser: (user) => set({ user, isAuthenticated: true, isInitializing: false }),
  clearUser: () => set({ user: null, isAuthenticated: false, isInitializing: false }),
  finishInitializing: () => set({ isInitializing: false }),
}));
