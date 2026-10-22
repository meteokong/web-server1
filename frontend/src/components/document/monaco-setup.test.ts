import { describe, expect, it } from "vitest";
import Editor, { loader } from "@monaco-editor/react";

/**
 * T099 smoke test: confirms `@monaco-editor/react` installs and bundles
 * cleanly under Vite/Vitest (ESM resolution, no missing peer deps). Full
 * in-browser rendering (worker loading, actual syntax highlighting) is
 * covered later by the manual browser test tasks — this only checks the
 * module graph resolves and exposes the pieces CodePanel (T100) needs.
 */
describe("Monaco Editor setup", () => {
  it("exposes the Editor component from @monaco-editor/react", () => {
    expect(Editor).toBeDefined();
    expect(typeof Editor).toBe("function");
  });

  it("exposes the loader used to configure the Monaco instance", () => {
    expect(loader).toBeDefined();
    expect(typeof loader.init).toBe("function");
  });
});
