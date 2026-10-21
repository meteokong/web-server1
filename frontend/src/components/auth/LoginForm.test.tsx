import { describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { LoginForm } from "./LoginForm";

describe("LoginForm", () => {
  it("renders email and password fields plus a submit button", () => {
    render(<LoginForm onSubmit={vi.fn()} />);

    expect(screen.getByLabelText(/이메일/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/비밀번호/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /로그인/i })).toBeInTheDocument();
  });

  it("calls onSubmit with the entered email and password", async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    const user = userEvent.setup();
    render(<LoginForm onSubmit={onSubmit} />);

    await user.type(screen.getByLabelText(/이메일/i), "test@example.com");
    await user.type(screen.getByLabelText(/비밀번호/i), "Sup3rSecret!");
    await user.click(screen.getByRole("button", { name: /로그인/i }));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith({
        email: "test@example.com",
        password: "Sup3rSecret!",
      });
    });
  });

  it("shows an error message when onSubmit rejects", async () => {
    const onSubmit = vi
      .fn()
      .mockRejectedValue(new Error("이메일 또는 비밀번호가 올바르지 않습니다."));
    const user = userEvent.setup();
    render(<LoginForm onSubmit={onSubmit} />);

    await user.type(screen.getByLabelText(/이메일/i), "test@example.com");
    await user.type(screen.getByLabelText(/비밀번호/i), "wrong");
    await user.click(screen.getByRole("button", { name: /로그인/i }));

    expect(
      await screen.findByText("이메일 또는 비밀번호가 올바르지 않습니다."),
    ).toBeInTheDocument();
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
    render(<LoginForm onSubmit={onSubmit} />);

    await user.type(screen.getByLabelText(/이메일/i), "test@example.com");
    await user.type(screen.getByLabelText(/비밀번호/i), "Sup3rSecret!");
    await user.click(screen.getByRole("button", { name: /로그인/i }));

    expect(screen.getByRole("button", { name: /로그인/i })).toBeDisabled();
    resolveSubmit();
  });
});
