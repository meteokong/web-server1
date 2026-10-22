import { useId, useState, type FormEvent } from "react";
import { Dialog } from "radix-ui";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { FileUpload } from "@/components/upload/FileUpload";
import { FolderUpload, type FolderUploadFile } from "@/components/upload/FolderUpload";
import { PasteCode } from "@/components/upload/PasteCode";

export type UploadMethod = "file" | "folder" | "paste";

export interface CreateTaskModalValues {
  title: string;
  description: string;
  uploadMethod: UploadMethod;
  files?: File[];
  pastedCode?: string;
}

export interface CreateTaskModalProps {
  open: boolean;
  onClose: () => void;
  /** Called with the entered values on submit. Reject to show an error. */
  onSubmit: (values: CreateTaskModalValues) => Promise<void>;
}

const MIN_TITLE_LENGTH = 5;

/**
 * Modal form for creating a new task, mirroring CreateProjectModal's
 * dialog/props shape. Adds an upload-method selector that conditionally
 * renders FileUpload (T076) / FolderUpload (T077) / PasteCode (T078), and
 * collects whichever is active into the submitted values alongside
 * title/description.
 */
export function CreateTaskModal({ open, onClose, onSubmit }: CreateTaskModalProps) {
  const titleId = useId();
  const descriptionId = useId();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [uploadMethod, setUploadMethod] = useState<UploadMethod>("file");
  const [files, setFiles] = useState<File[]>([]);
  const [pastedCode, setPastedCode] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  function handleUploadMethodChange(nextMethod: UploadMethod) {
    setUploadMethod(nextMethod);
    setFiles([]);
    setPastedCode("");
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    if (title.trim().length < MIN_TITLE_LENGTH) {
      setError(`제목은 ${MIN_TITLE_LENGTH}자 이상이어야 합니다.`);
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit({
        title,
        description,
        uploadMethod,
        ...(uploadMethod === "paste" ? { pastedCode } : { files }),
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "태스크 생성에 실패했습니다.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Dialog.Root
      open={open}
      onOpenChange={(nextOpen) => {
        if (!nextOpen) onClose();
      }}
    >
      <Dialog.Portal>
        <Dialog.Overlay />
        <Dialog.Content>
          <Dialog.Title>새 태스크 만들기</Dialog.Title>
          <form onSubmit={handleSubmit} noValidate>
            <div>
              <label htmlFor={titleId}>제목</label>
              <Input
                id={titleId}
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor={descriptionId}>설명</label>
              <Input
                id={descriptionId}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>

            <fieldset>
              <legend>업로드 방식</legend>
              <label>
                <input
                  type="radio"
                  name="uploadMethod"
                  checked={uploadMethod === "file"}
                  onChange={() => handleUploadMethodChange("file")}
                />
                파일 업로드
              </label>
              <label>
                <input
                  type="radio"
                  name="uploadMethod"
                  checked={uploadMethod === "folder"}
                  onChange={() => handleUploadMethodChange("folder")}
                />
                폴더 업로드
              </label>
              <label>
                <input
                  type="radio"
                  name="uploadMethod"
                  checked={uploadMethod === "paste"}
                  onChange={() => handleUploadMethodChange("paste")}
                />
                코드 붙여넣기
              </label>
            </fieldset>

            {uploadMethod === "file" && <FileUpload onFilesSelected={setFiles} />}
            {uploadMethod === "folder" && (
              <FolderUpload
                onFilesSelected={(picked: FolderUploadFile[]) =>
                  setFiles(picked.map((p) => p.file))
                }
              />
            )}
            {uploadMethod === "paste" && (
              <PasteCode onChange={({ code }) => setPastedCode(code)} />
            )}

            {error && <p role="alert">{error}</p>}
            <Button type="button" variant="outline" onClick={onClose}>
              취소
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              생성
            </Button>
          </form>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
