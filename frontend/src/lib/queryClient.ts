import { QueryClient } from "@tanstack/react-query";

/**
 * Shared TanStack Query client. Provided to the app once via
 * QueryClientProvider in main.tsx; feature code (project-service,
 * task-service, ...) calls useQuery/useMutation against this cache.
 */
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Data is considered fresh for 30s before a background refetch is
      // triggered — avoids refetching on every component remount while
      // still picking up changes reasonably quickly (stale-while-revalidate,
      // per research.md's frontend caching strategy).
      staleTime: 30_000,
      // Keep unused query data around for 5 minutes before garbage
      // collection, so navigating back to a page (e.g. Dashboard ->
      // ProjectDetail -> Dashboard) can show cached data instantly.
      gcTime: 5 * 60_000,
      // Network requests, not local state: retry transient failures once,
      // but don't hammer a server that's actually down.
      retry: 1,
      refetchOnWindowFocus: false,
    },
    mutations: {
      // Mutations (create/update/delete) must not silently retry — a
      // failed POST could otherwise double-submit on an automatic retry.
      retry: 0,
    },
  },
});
