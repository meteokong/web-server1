import Editor from "@monaco-editor/react";

export interface CodePanelProps {
  /** The uploaded code's content to display. */
  code: string;
  /** Detected language (task-service's UploadedCode.detectedLanguage), used for syntax highlighting. */
  language: string;
}

/**
 * CodePanel (T100): shows the task's uploaded code in a read-only Monaco
 * Editor with language-aware syntax highlighting. The actual code content
 * comes from getTaskCode (task-service.ts, T075) — this component only
 * renders what it's given.
 */
export default function CodePanel({ code, language }: CodePanelProps) {
  return (
    <div className="h-full">
      <Editor
        height="100%"
        language={language || "plaintext"}
        value={code}
        options={{ readOnly: true, minimap: { enabled: false } }}
      />
    </div>
  );
}
