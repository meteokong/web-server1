import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import DocumentViewer from "./DocumentViewer";
import type { DocumentContent } from "@/types/document";

vi.mock("@monaco-editor/react", () => ({
  default: (props: { value: string }) => <div data-testid="monaco-editor">{props.value}</div>,
}));

const content: DocumentContent = {
  chapter1: { title: "What This Code Does", summary: "배열을 정렬한다." },
  chapter2: { title: "Prerequisites Knowledge", concepts: [] },
  chapter3: { title: "Code Structure Overview", flowchart: "", fileBreakdown: {} },
  chapter4: { title: "Line-by-Line Explanation", explanations: [] },
  chapter5: { title: "Execution Flow Simulation", steps: [] },
  chapter6: { title: "Core Concepts Summary", concepts: [] },
  chapter7: { title: "Common Mistakes", mistakes: [] },
};

function setScrollMetrics(
  el: HTMLElement,
  metrics: { scrollTop: number; scrollHeight: number; clientHeight: number },
) {
  Object.defineProperty(el, "scrollTop", {
    value: metrics.scrollTop,
    writable: true,
    configurable: true,
  });
  Object.defineProperty(el, "scrollHeight", {
    value: metrics.scrollHeight,
    configurable: true,
  });
  Object.defineProperty(el, "clientHeight", {
    value: metrics.clientHeight,
    configurable: true,
  });
}

describe("DocumentViewer", () => {
  it("renders the code in the left pane via CodePanel", () => {
    render(<DocumentViewer code="print(1)" language="python" content={content} />);

    expect(screen.getByTestId("monaco-editor")).toHaveTextContent("print(1)");
  });

  it("renders the explanation content in the right pane via ExplanationPanel", () => {
    render(<DocumentViewer code="print(1)" language="python" content={content} />);

    expect(screen.getByText("배열을 정렬한다.")).toBeInTheDocument();
  });

  it("syncs the explanation pane's scroll position proportionally when the code pane scrolls", () => {
    render(<DocumentViewer code="print(1)" language="python" content={content} />);

    const codePane = screen.getByTestId("document-viewer-code-pane");
    const explanationPane = screen.getByTestId("document-viewer-explanation-pane");

    setScrollMetrics(codePane, { scrollTop: 50, scrollHeight: 300, clientHeight: 100 });
    setScrollMetrics(explanationPane, { scrollTop: 0, scrollHeight: 600, clientHeight: 100 });

    fireEvent.scroll(codePane);

    // codePane scrolled to 50/(300-100) = 25% -> explanationPane should move
    // to 25% of its own (600-100) scrollable range = 125.
    expect(explanationPane.scrollTop).toBe(125);
  });

  it("syncs the code pane's scroll position proportionally when the explanation pane scrolls", () => {
    render(<DocumentViewer code="print(1)" language="python" content={content} />);

    const codePane = screen.getByTestId("document-viewer-code-pane");
    const explanationPane = screen.getByTestId("document-viewer-explanation-pane");

    setScrollMetrics(explanationPane, { scrollTop: 250, scrollHeight: 600, clientHeight: 100 });
    setScrollMetrics(codePane, { scrollTop: 0, scrollHeight: 300, clientHeight: 100 });

    fireEvent.scroll(explanationPane);

    // explanationPane scrolled to 250/(600-100) = 50% -> codePane should
    // move to 50% of its own (300-100) scrollable range = 100.
    expect(codePane.scrollTop).toBe(100);
  });
});
