import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { FolderUpload } from "./FolderUpload";

function makeFile(name: string, relativePath: string) {
  const file = new File(["code"], name, { type: "text/plain" });
  Object.defineProperty(file, "webkitRelativePath", { value: relativePath });
  return file;
}

describe("FolderUpload", () => {
  it("renders a visible button and a hidden folder-picker input", () => {
    render(<FolderUpload onFilesSelected={vi.fn()} />);

    const input = screen.getByLabelText(/폴더 선택/i) as HTMLInputElement;
    expect(input).toBeInTheDocument();
    expect(input.type).toBe("file");
    expect(input.getAttribute("webkitdirectory")).not.toBeNull();
    expect(input.getAttribute("directory")).not.toBeNull();
  });

  it("calls onFilesSelected with each file paired with its relativePath", () => {
    const onFilesSelected = vi.fn();
    render(<FolderUpload onFilesSelected={onFilesSelected} />);

    const fileA = makeFile("a.py", "myproject/a.py");
    const fileB = makeFile("b.py", "myproject/sub/b.py");
    const input = screen.getByLabelText(/폴더 선택/i) as HTMLInputElement;

    Object.defineProperty(input, "files", { value: [fileA, fileB] });
    input.dispatchEvent(new Event("change", { bubbles: true }));

    expect(onFilesSelected).toHaveBeenCalledWith([
      { file: fileA, relativePath: "myproject/a.py" },
      { file: fileB, relativePath: "myproject/sub/b.py" },
    ]);
  });
});
