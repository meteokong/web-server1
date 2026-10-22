import { useRef } from "react";
import type { DocumentContent } from "@/types/document";
import CodePanel from "./CodePanel";
import ExplanationPanel from "./ExplanationPanel";

export interface DocumentViewerProps {
  code: string;
  language: string;
  content: DocumentContent;
}

/**
 * DocumentViewer (T105): 2-column layout — the uploaded code (CodePanel) on
 * the left, the generated explanation (ExplanationPanel) on the right —
 * with scroll sync between the two: scrolling one pane moves the other by
 * the same proportion of its own scrollable range. This is a ratio-based
 * sync, not a line-level mapping (deliberately simple per the brief).
 */
export default function DocumentViewer({ code, language, content }: DocumentViewerProps) {
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
