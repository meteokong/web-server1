import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { FileUpload } from "./FileUpload";

function makeFile(name: string, content = "console.log(1);") {
  return new File([content], name, { type: "text/plain" });
}

describe("FileUpload", () => {
  it("renders a visible button and a hidden multi-file input", () => {
    render(<FileUpload onFilesSelected={vi.fn()} />);

    const input = screen.getByLabelText(/파일 선택/i) as HTMLInputElement;
    expect(input).toBeInTheDocument();
    expect(input.type).toBe("file");
    expect(input.multiple).toBe(true);
  });

  it("calls onFilesSelected with the chosen files via the file input", async () => {
    const onFilesSelected = vi.fn();
    const user = userEvent.setup();
    render(<FileUpload onFilesSelected={onFilesSelected} />);

    const file = makeFile("a.py");
    const input = screen.getByLabelText(/파일 선택/i);
    await user.upload(input, file);

    expect(onFilesSelected).toHaveBeenCalledWith([file]);
  });

  it("calls onFilesSelected with dropped files", () => {
    const onFilesSelected = vi.fn();
    render(<FileUpload onFilesSelected={onFilesSelected} />);

    const file = makeFile("b.js");
    const dropzone = screen.getByTestId("file-upload-dropzone");

    const dataTransfer = { files: [file] };
    dropzone.dispatchEvent(
      Object.assign(new Event("drop", { bubbles: true, cancelable: true }), {
        dataTransfer,
      }),
    );

    expect(onFilesSelected).toHaveBeenCalledWith([file]);
  });
});
