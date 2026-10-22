import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import CodePanel from "./CodePanel";

/**
 * Monaco's real Editor needs a browser environment (canvas, workers) that
 * jsdom doesn't provide, so it's mocked here to a simple element exposing
 * the props CodePanel passes down — the same approach used for other
 * heavy third-party widgets in this codebase. Real in-browser rendering is
 * covered by the manual browser test tasks.
 */
vi.mock("@monaco-editor/react", () => ({
  default: (props: { value: string; language?: string; options?: Record<string, unknown> }) => (
    <div
      data-testid="monaco-editor"
      data-language={props.language}
      data-readonly={String(props.options?.readOnly)}
    >
      {props.value}
    </div>
  ),
}));

describe("CodePanel", () => {
  it("renders the given code content inside the editor", () => {
    render(<CodePanel code="print('hello')" language="python" />);

    expect(screen.getByTestId("monaco-editor")).toHaveTextContent("print('hello')");
  });

  it("passes the detected language through for syntax highlighting", () => {
    render(<CodePanel code="print('hello')" language="python" />);

    expect(screen.getByTestId("monaco-editor")).toHaveAttribute("data-language", "python");
  });

  it("renders the editor as read-only", () => {
    render(<CodePanel code="print('hello')" language="python" />);

    expect(screen.getByTestId("monaco-editor")).toHaveAttribute("data-readonly", "true");
  });

  it("falls back to plain text language when none is given", () => {
    render(<CodePanel code="no lang" language="" />);

    expect(screen.getByTestId("monaco-editor")).toHaveAttribute("data-language", "plaintext");
  });
});
