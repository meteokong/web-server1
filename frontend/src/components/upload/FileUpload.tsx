import { useId, useRef, type DragEvent } from "react";
import { Button } from "@/components/ui/button";

export interface FileUploadProps {
  /** Called with the files picked (via the dialog or drag-and-drop). */
  onFilesSelected: (files: File[]) => void;
}

/**
 * Drag-and-drop zone + a hidden file input behind a visible button, for
 * the "파일 업로드" method of CreateTaskModal (T081). Collects files only —
 * no upload/validation logic, that's the parent's job.
 */
export function FileUpload({ onFilesSelected }: FileUploadProps) {
  const inputId = useId();
  const inputRef = useRef<HTMLInputElement>(null);

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    const files = Array.from(event.dataTransfer.files);
    if (files.length > 0) onFilesSelected(files);
  }

  function handleDragOver(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
  }

  return (
    <div data-testid="file-upload-dropzone" onDrop={handleDrop} onDragOver={handleDragOver}>
      <p>파일을 드래그해서 놓거나 버튼을 눌러 선택하세요.</p>
      <label htmlFor={inputId} style={{ display: "none" }}>
        파일 선택
      </label>
      <input
        ref={inputRef}
        id={inputId}
        type="file"
        multiple
        style={{ display: "none" }}
        onChange={(e) => {
          const files = Array.from(e.target.files ?? []);
          if (files.length > 0) onFilesSelected(files);
        }}
      />
      <Button type="button" onClick={() => inputRef.current?.click()}>
        파일 선택
      </Button>
    </div>
  );
}
