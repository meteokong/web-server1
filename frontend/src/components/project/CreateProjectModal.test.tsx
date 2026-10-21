import { describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { CreateProjectModal } from "./CreateProjectModal";

describe("CreateProjectModal", () => {
  it("renders nothing when closed", () => {
    render(<CreateProjectModal open={false} onClose={vi.fn()} onSubmit={vi.fn()} />);

    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("renders a title field, optional description field, and submit button when open", () => {
    render(<CreateProjectModal open={true} onClose={vi.fn()} onSubmit={vi.fn()} />);

    expect(screen.getByRole("dialog")).toBeInTheDocument();
    expect(screen.getByLabelText(/제목/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/설명/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /생성/i })).toBeInTheDocument();
  });

  it("calls onSubmit with the entered title and description", async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    const user = userEvent.setup();
    render(<CreateProjectModal open={true} onClose={vi.fn()} onSubmit={onSubmit} />);

    await user.type(screen.getByLabelText(/제목/i), "React 학습");
    await user.type(screen.getByLabelText(/설명/i), "기초부터 심화까지");
    await user.click(screen.getByRole("button", { name: /생성/i }));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith({
        title: "React 학습",
        description: "기초부터 심화까지",
      });
    });
  });

  it("shows an error message when onSubmit rejects", async () => {
    const onSubmit = vi.fn().mockRejectedValue(new Error("제목은 비워둘 수 없습니다."));
    const user = userEvent.setup();
    render(<CreateProjectModal open={true} onClose={vi.fn()} onSubmit={onSubmit} />);

    await user.type(screen.getByLabelText(/제목/i), "x");
    await user.click(screen.getByRole("button", { name: /생성/i }));

    expect(await screen.findByText("제목은 비워둘 수 없습니다.")).toBeInTheDocument();
  });

  it("calls onClose when the cancel button is clicked", async () => {
    const onClose = vi.fn();
    const user = userEvent.setup();
    render(<CreateProjectModal open={true} onClose={onClose} onSubmit={vi.fn()} />);

    await user.click(screen.getByRole("button", { name: /취소/i }));

    expect(onClose).toHaveBeenCalled();
  });
});
