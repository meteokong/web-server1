import { useEffect, useId, useRef } from "react";
import { Button } from "@/components/ui/button";

export interface FolderUploadFile {
  file: File;
  relativePath: string;
}

export interface FolderUploadProps {
  /** Called with every file in the picked folder, paired with its path relative to it. */
  onFilesSelected: (files: FolderUploadFile[]) => void;
}

/**
 * Same shape as FileUpload (T076), but picks a whole folder. `webkitdirectory`/
 * `directory` aren't typed as JSX props on <input>, so they're set via a ref
 * effect instead. Each file's `webkitRelativePath` (e.g. "myproject/sub/b.py")
 * is preserved for the parent (CreateTaskModal, T081) to send alongside the
 * upload.
 */
export function FolderUpload({ onFilesSelected }: FolderUploadProps) {
  const inputId = useId();
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const input = inputRef.current;
    if (!input) return;
    input.setAttribute("webkitdirectory", "");
    input.setAttribute("directory", "");
  }, []);

  function handleChange(files: FileList | null) {
    const picked = Array.from(files ?? []);
    if (picked.length === 0) return;
    onFilesSelected(
      picked.map((file) => ({
        file,
        relativePath: file.webkitRelativePath || file.name,
      })),
    );
  }

  return (
    <div>
      <p>폴더를 선택하면 하위 파일 구조를 그대로 유지해서 업로드합니다.</p>
      <label htmlFor={inputId} style={{ display: "none" }}>
        폴더 선택
      </label>
      <input
        ref={inputRef}
        id={inputId}
        type="file"
        multiple
        style={{ display: "none" }}
        onChange={(e) => handleChange(e.target.files)}
      />
      <Button type="button" onClick={() => inputRef.current?.click()}>
        폴더 선택
      </Button>
    </div>
  );
}
