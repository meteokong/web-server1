import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import Chapter1 from "./Chapter1";
import type { Chapter1Content } from "@/types/document";

const content: Chapter1Content = {
  title: "What This Code Does",
  summary: "이 코드는 배열을 버블 정렬로 오름차순 정렬한다.",
};

describe("Chapter1", () => {
  it("renders the chapter's title", () => {
    render(<Chapter1 content={content} />);

    expect(screen.getByText("What This Code Does")).toBeInTheDocument();
  });

  it("renders the one-sentence summary", () => {
    render(<Chapter1 content={content} />);

    expect(screen.getByText(content.summary)).toBeInTheDocument();
  });
});
