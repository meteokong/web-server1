import { describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { RegisterForm } from "./RegisterForm";

describe("RegisterForm", () => {
  it("renders email and password fields plus a submit button", () => {
    render(<RegisterForm onSubmit={vi.fn()} />);

    expect(screen.getByLabelText(/이메일/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/비밀번호/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /가입/i })).toBeInTheDocument();
  });

  it("calls onSubmit with the entered email and password", async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    const user = userEvent.setup();
    render(<RegisterForm onSubmit={onSubmit} />);

    await user.type(screen.getByLabelText(/이메일/i), "test@example.com");
    await user.type(screen.getByLabelText(/비밀번호/i), "Sup3rSecret!");
    await user.click(screen.getByRole("button", { name: /가입/i }));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith({
        email: "test@example.com",
        password: "Sup3rSecret!",
      });
    });
  });

  it("shows an error message when onSubmit rejects", async () => {
    const onSubmit = vi.fn().mockRejectedValue(new Error("이미 가입된 이메일입니다."));
    const user = userEvent.setup();
    render(<RegisterForm onSubmit={onSubmit} />);

    await user.type(screen.getByLabelText(/이메일/i), "dup@example.com");
    await user.type(screen.getByLabelText(/비밀번호/i), "Sup3rSecret!");
    await user.click(screen.getByRole("button", { name: /가입/i }));

    expect(await screen.findByText("이미 가입된 이메일입니다.")).toBeInTheDocument();
  });

  it("disables the submit button while submitting", async () => {
    let resolveSubmit: () => void = () => {};
    const onSubmit = vi.fn(
      () =>
        new Promise<void>((resolve) => {
          resolveSubmit = resolve;
        }),
    );
    const user = userEvent.setup();
    render(<RegisterForm onSubmit={onSubmit} />);

    await user.type(screen.getByLabelText(/이메일/i), "test@example.com");
    await user.type(screen.getByLabelText(/비밀번호/i), "Sup3rSecret!");
    await user.click(screen.getByRole("button", { name: /가입/i }));

    expect(screen.getByRole("button", { name: /가입/i })).toBeDisabled();
    resolveSubmit();
  });
});
