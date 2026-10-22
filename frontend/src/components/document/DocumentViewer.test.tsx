import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import DocumentViewer from "./DocumentViewer";
import { getDocument, getDocumentStatus } from "@/services/document-service";
import { getTaskCode } from "@/services/task-service";
import type { DocumentContent, DocumentStatus, TaskDocument } from "@/types/document";
import type { TaskCode } from "@/services/task-service";

/**
 * Monaco needs a real browser (canvas/workers) jsdom doesn't provide, so
 * it's mocked the same way CodePanel.test.tsx does.
 */
vi.mock("@monaco-editor/react", () => ({
  default: (props: { value: string }) => <div data-testid="monaco-editor">{props.value}</div>,
}));

vi.mock("@/services/document-service", () => ({
  getDocumentStatus: vi.fn(),
  getDocument: vi.fn(),
}));

vi.mock("@/services/task-service", () => ({
  getTaskCode: vi.fn(),
}));

const mockedGetDocumentStatus = getDocumentStatus as unknown as ReturnType<typeof vi.fn>;
const mockedGetDocument = getDocument as unknown as ReturnType<typeof vi.fn>;
const mockedGetTaskCode = getTaskCode as unknown as ReturnType<typeof vi.fn>;

function status(overrides: Partial<DocumentStatus>): DocumentStatus {
  return {
    taskId: "task-1",
    generationStatus: "pending",
    generationError: null,
    generationStartedAt: null,
    generationCompletedAt: null,
    ...overrides,
  };
}

const content: DocumentContent = {
  chapter1: { title: "What This Code Does", summary: "배열을 정렬한다." },
  chapter2: { title: "Prerequisites Knowledge", concepts: [] },
  chapter3: { title: "Code Structure Overview", flowchart: "", fileBreakdown: {} },
  chapter4: { title: "Line-by-Line Explanation", explanations: [] },
  chapter5: { title: "Execution Flow Simulation", steps: [] },
  chapter6: { title: "Core Concepts Summary", concepts: [] },
  chapter7: { title: "Common Mistakes", mistakes: [] },
};

const taskCode: TaskCode = {
  uploadedCode: {
    detectedLanguage: "python",
    complexityLevel: "beginner",
    totalLines: 10,
    totalFiles: 1,
    uploadSizeBytes: 100,
  },
  files: [{ fileName: "main.py", filePath: null, fileExtension: "py", fileSizeBytes: 100 }],
};

function renderViewer() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <DocumentViewer taskId="task-1" />
    </QueryClientProvider>,
  );
}

describe("DocumentViewer", () => {
  it("shows a generating/loading indicator while status is pending", async () => {
    mockedGetDocumentStatus.mockResolvedValue(status({ generationStatus: "pending" }));

    renderViewer();

    expect(await screen.findByRole("status")).toHaveTextContent(/생성/);
  });

  it("shows a generating/loading indicator while status is in_progress", async () => {
    mockedGetDocumentStatus.mockResolvedValue(status({ generationStatus: "in_progress" }));

    renderViewer();

    expect(await screen.findByRole("status")).toHaveTextContent(/생성/);
  });

  it("shows an error message when generation failed", async () => {
    mockedGetDocumentStatus.mockResolvedValue(
      status({ generationStatus: "failed", generationError: "Gemini API 오류" }),
    );

    renderViewer();

    expect(await screen.findByRole("alert")).toHaveTextContent("Gemini API 오류");
  });

  it("fetches the document + code and renders the 2-column view once completed", async () => {
    mockedGetDocumentStatus.mockResolvedValue(status({ generationStatus: "completed" }));
    mockedGetDocument.mockResolvedValue({
      taskId: "task-1",
      generationStatus: "completed",
      generationError: null,
      content,
    } satisfies TaskDocument);
    mockedGetTaskCode.mockResolvedValue(taskCode);

    renderViewer();

    expect(await screen.findByText("배열을 정렬한다.")).toBeInTheDocument();
    expect(screen.getByTestId("monaco-editor")).toHaveTextContent("main.py");
  });

  it("syncs the two panes' scroll position proportionally once the document is shown", async () => {
    mockedGetDocumentStatus.mockResolvedValue(status({ generationStatus: "completed" }));
    mockedGetDocument.mockResolvedValue({
      taskId: "task-1",
      generationStatus: "completed",
      generationError: null,
      content,
    } satisfies TaskDocument);
    mockedGetTaskCode.mockResolvedValue(taskCode);

    renderViewer();
    await screen.findByText("배열을 정렬한다.");

    const codePane = screen.getByTestId("document-viewer-code-pane");
    const explanationPane = screen.getByTestId("document-viewer-explanation-pane");

    Object.defineProperty(codePane, "scrollTop", { value: 50, writable: true, configurable: true });
    Object.defineProperty(codePane, "scrollHeight", { value: 300, configurable: true });
    Object.defineProperty(codePane, "clientHeight", { value: 100, configurable: true });
    Object.defineProperty(explanationPane, "scrollTop", {
      value: 0,
      writable: true,
      configurable: true,
    });
    Object.defineProperty(explanationPane, "scrollHeight", { value: 600, configurable: true });
    Object.defineProperty(explanationPane, "clientHeight", { value: 100, configurable: true });

    fireEvent.scroll(codePane);

    expect(explanationPane.scrollTop).toBe(125);
  });
});
