import { describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { CreateTaskModal } from "./CreateTaskModal";

describe("CreateTaskModal", () => {
  it("renders nothing when closed", () => {
    render(<CreateTaskModal open={false} onClose={vi.fn()} onSubmit={vi.fn()} />);

    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("renders a title field and the 3 upload-method options when open", () => {
    render(<CreateTaskModal open={true} onClose={vi.fn()} onSubmit={vi.fn()} />);

    expect(screen.getByRole("dialog")).toBeInTheDocument();
    expect(screen.getByLabelText(/제목/i)).toBeInTheDocument();
    expect(screen.getByRole("radio", { name: /파일 업로드/i })).toBeInTheDocument();
    expect(screen.getByRole("radio", { name: /폴더 업로드/i })).toBeInTheDocument();
    expect(screen.getByRole("radio", { name: /코드 붙여넣기/i })).toBeInTheDocument();
  });

  it("defaults to the file upload method and shows FileUpload's picker", () => {
    render(<CreateTaskModal open={true} onClose={vi.fn()} onSubmit={vi.fn()} />);

    expect(screen.getByLabelText(/파일 선택/i)).toBeInTheDocument();
  });

  it("switches to PasteCode's fields when the paste-code option is selected", async () => {
    const user = userEvent.setup();
    render(<CreateTaskModal open={true} onClose={vi.fn()} onSubmit={vi.fn()} />);

    await user.click(screen.getByRole("radio", { name: /코드 붙여넣기/i }));

    expect(screen.getByLabelText(/^코드$/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/언어/i)).toBeInTheDocument();
  });

  it("shows a validation error when the title is shorter than 5 characters", async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    render(<CreateTaskModal open={true} onClose={vi.fn()} onSubmit={onSubmit} />);

    await user.type(screen.getByLabelText(/제목/i), "짧음");
    await user.click(screen.getByRole("radio", { name: /코드 붙여넣기/i }));
    await user.type(screen.getByLabelText(/^코드$/i), "print(1)");
    await user.click(screen.getByRole("button", { name: /생성/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent(/5자/);
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("calls onSubmit with title/description/uploadMethod/pastedCode for a paste submission", async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    const user = userEvent.setup();
    render(<CreateTaskModal open={true} onClose={vi.fn()} onSubmit={onSubmit} />);

    await user.type(screen.getByLabelText(/제목/i), "배열 정렬 연습");
    await user.click(screen.getByRole("radio", { name: /코드 붙여넣기/i }));
    await user.type(screen.getByLabelText(/^코드$/i), "print(1)");
    await user.click(screen.getByRole("button", { name: /생성/i }));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          title: "배열 정렬 연습",
          uploadMethod: "paste",
          pastedCode: "print(1)",
        }),
      );
    });
  });

  it("calls onClose when the cancel button is clicked", async () => {
    const onClose = vi.fn();
    const user = userEvent.setup();
    render(<CreateTaskModal open={true} onClose={onClose} onSubmit={vi.fn()} />);

    await user.click(screen.getByRole("button", { name: /취소/i }));

    expect(onClose).toHaveBeenCalled();
  });
});
