import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { PasteCode } from "./PasteCode";

describe("PasteCode", () => {
  it("renders a textarea for code and a language select", () => {
    render(<PasteCode onChange={vi.fn()} />);

    expect(screen.getByLabelText(/코드/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/언어/i)).toBeInTheDocument();
  });

  it("offers the backend's supported languages as select options", () => {
    render(<PasteCode onChange={vi.fn()} />);

    const select = screen.getByLabelText(/언어/i) as HTMLSelectElement;
    const values = Array.from(select.options).map((o) => o.value);

    expect(values).toEqual(
      expect.arrayContaining([
        "python",
        "javascript",
        "typescript",
        "java",
        "cpp",
        "c",
        "html",
        "css",
        "text",
        "markdown",
      ]),
    );
  });

  it("calls onChange with the code and language whenever either changes", async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();
    render(<PasteCode onChange={onChange} />);

    await user.type(screen.getByLabelText(/코드/i), "x");
    expect(onChange).toHaveBeenLastCalledWith({ code: "x", language: "python" });

    await user.selectOptions(screen.getByLabelText(/언어/i), "javascript");
    expect(onChange).toHaveBeenLastCalledWith({ code: "x", language: "javascript" });
  });
});
