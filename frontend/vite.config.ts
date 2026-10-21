import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import path from "node:path";
import { defineConfig } from "vite";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  // Read .env from the repo root, not frontend/, so the whole project
  // (backend + frontend) shares one .env file (see quickstart.md).
  envDir: "..",
  resolve: {
    alias: {
      // "@/..." import alias, required by shadcn/ui components.
      "@": path.resolve(import.meta.dirname, "./src"),
    },
  },
});
