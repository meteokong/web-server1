import { useRef } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  documentStatusPollIntervalMs,
  getDocument,
  getDocumentStatus,
} from "@/services/document-service";
import { getTaskCode } from "@/services/task-service";
import type { DocumentContent } from "@/types/document";
import CodePanel from "./CodePanel";
import ExplanationPanel from "./ExplanationPanel";

export interface DocumentViewerProps {
  taskId: string;
}

/**
 * DocumentViewer (T105/T107): shows a task's generated learning document.
 *
 * Owns its own data: polls GET .../document/status (document-service,
 * T106) via `refetchInterval` until generation reaches a terminal state
 * (documentStatusPollIntervalMs returns `false` there, stopping the poll),
 * showing a "generating..." indicator meanwhile; on "failed" it shows the
 * generation error; on "completed" it fetches the full document + the
 * task's uploaded code and renders the 2-column CodePanel/ExplanationPanel
 * layout with scroll sync (same ratio-based sync introduced in T105).
 */
export default function DocumentViewer({ taskId }: DocumentViewerProps) {
  const { data: status } = useQuery({
    queryKey: ["tasks", "document-status", taskId],
    queryFn: () => getDocumentStatus(taskId),
    refetchInterval: (query) => documentStatusPollIntervalMs(query.state.data?.generationStatus),
  });

  const isCompleted = status?.generationStatus === "completed";

  const { data: document } = useQuery({
    queryKey: ["tasks", "document", taskId],
    queryFn: () => getDocument(taskId),
    enabled: isCompleted,
  });

  const { data: taskCode } = useQuery({
    queryKey: ["tasks", "code", taskId],
    queryFn: () => getTaskCode(taskId),
    enabled: isCompleted,
  });

  if (!status || status.generationStatus === "pending" || status.generationStatus === "in_progress") {
    return (
      <div role="status">
        <p>문서를 생성하는 중입니다...</p>
      </div>
    );
  }

  if (status.generationStatus === "failed") {
    return <p role="alert">{status.generationError ?? "문서 생성에 실패했습니다."}</p>;
  }

  if (!document?.content || !taskCode) {
    return (
      <div role="status">
        <p>문서를 불러오는 중입니다...</p>
      </div>
    );
  }

  // The uploaded-code endpoint (getTaskCode) only exposes file metadata,
  // not file content, so the code pane shows the uploaded file names
  // rather than invented source text.
  const code = taskCode.files.map((file) => file.fileName).join("\n") || "코드 파일이 없습니다.";

  return (
    <TwoColumnDocument
      code={code}
      language={taskCode.uploadedCode.detectedLanguage}
      content={document.content}
    />
  );
}

function TwoColumnDocument({
  code,
  language,
  content,
}: {
  code: string;
  language: string;
  content: DocumentContent;
}) {
  const codePaneRef = useRef<HTMLDivElement>(null);
  const explanationPaneRef = useRef<HTMLDivElement>(null);
  // Scrolling one pane programmatically sets the other pane's scrollTop,
  // which would otherwise fire that pane's own scroll handler and sync
  // back — this flag skips exactly that one echoed event.
  const suppressNextScrollOn = useRef<"code" | "explanation" | null>(null);

  function syncFrom(source: "code" | "explanation") {
    return () => {
      if (suppressNextScrollOn.current === source) {
        suppressNextScrollOn.current = null;
        return;
      }

      const sourceEl = source === "code" ? codePaneRef.current : explanationPaneRef.current;
      const targetEl = source === "code" ? explanationPaneRef.current : codePaneRef.current;
      if (!sourceEl || !targetEl) return;

      const sourceRange = sourceEl.scrollHeight - sourceEl.clientHeight;
      const targetRange = targetEl.scrollHeight - targetEl.clientHeight;
      if (sourceRange <= 0) return;

      const ratio = sourceEl.scrollTop / sourceRange;
      suppressNextScrollOn.current = source === "code" ? "explanation" : "code";
      targetEl.scrollTop = ratio * targetRange;
    };
  }

  return (
    <div style={{ display: "flex", height: "100%" }}>
      <div
        ref={codePaneRef}
        data-testid="document-viewer-code-pane"
        onScroll={syncFrom("code")}
        style={{ flex: 1, overflow: "auto" }}
      >
        <CodePanel code={code} language={language} />
      </div>
      <div
        ref={explanationPaneRef}
        data-testid="document-viewer-explanation-pane"
        onScroll={syncFrom("explanation")}
        style={{ flex: 1, overflow: "auto" }}
      >
        <ExplanationPanel content={content} />
      </div>
    </div>
  );
}
