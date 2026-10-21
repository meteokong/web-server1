import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import path from "node:path";
import { defineConfig } from "vitest/config";

// Separate from vite.config.ts (which drives the real app build) so the
// test runner's config can evolve independently. Shares the same plugins
// and "@/..." alias so components under test resolve identically to how
// they resolve in the real app.
export default defineConfig({
  plugins: [react(), tailwindcss()],
  envDir: "..",
  resolve: {
    alias: {
      "@": path.resolve(import.meta.dirname, "./src"),
    },
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./src/test/setup.ts"],
  },
});
