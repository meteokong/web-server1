import { useEffect } from "react";
import { getCurrentUser } from "@/services/auth-service";
import { useAuthStore } from "@/stores/auth-store";

/**
 * Mount this once near the app root (e.g. in App.tsx). On mount it asks
 * the backend "is there already a valid session?" via GET /auth/me —
 * this is how a page refresh (or opening the app in a new tab) finds
 * out the user is still logged in, since the access/refresh tokens live
 * in HTTPOnly cookies the store can't inspect on its own.
 *
 * Either way (logged in or not) it calls finishInitializing() when the
 * check settles, which is what lets ProtectedRoute (T037) stop
 * rendering nothing and make its redirect-vs-render decision.
 *
 * The other half of "auto refresh" — retrying a request once after a
 * 401 triggers POST /auth/refresh — lives in api-client.ts's response
 * interceptor (T038), since that needs to intercept every API call, not
 * just this initial check. See the comment there for the full design.
 */
export function useAuth() {
  useEffect(() => {
    let cancelled = false;

    async function checkSession() {
      try {
        const user = await getCurrentUser();
        if (!cancelled) {
          useAuthStore.getState().setUser(user);
        }
      } catch {
        // No valid session cookie (or it's expired and refresh - via the
        // api-client interceptor - couldn't save it either). Nothing to
        // do: the store already starts as "logged out".
        if (!cancelled) {
          useAuthStore.getState().clearUser();
        }
      } finally {
        if (!cancelled) {
          useAuthStore.getState().finishInitializing();
        }
      }
    }

    void checkSession();

    return () => {
      cancelled = true;
    };
  }, []);
}
