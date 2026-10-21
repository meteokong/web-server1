import { useId, useState, type FormEvent } from "react";
import { Dialog } from "radix-ui";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export interface CreateProjectModalValues {
  title: string;
  description: string;
}

export interface CreateProjectModalProps {
  open: boolean;
  onClose: () => void;
  /** Called with the entered values on submit. Reject to show an error. */
  onSubmit: (values: CreateProjectModalValues) => Promise<void>;
}

/**
 * Modal form for creating a new project. Presentational/interactive only
 * — knows nothing about the projects API, just collects title/description
 * and delegates to onSubmit, which the Dashboard page (T056) wires to
 * project-service's createProject().
 */
export function CreateProjectModal({ open, onClose, onSubmit }: CreateProjectModalProps) {
  const titleId = useId();
  const descriptionId = useId();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await onSubmit({ title, description });
    } catch (err) {
      setError(err instanceof Error ? err.message : "프로젝트 생성에 실패했습니다.");
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
          <Dialog.Title>새 프로젝트 만들기</Dialog.Title>
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
