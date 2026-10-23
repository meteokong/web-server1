import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import Chapter4 from "./Chapter4";
import type { Chapter4Content } from "@/types/document";

const content: Chapter4Content = {
  title: "Line-by-Line Explanation",
  explanations: [
    {
      line: 1,
      code: "def factorial(n):",
      explanation: "factorial이라는 함수를 정의한다.",
      analogy: "요리 레시피 제목을 적는 것과 같다.",
      alternativeExample: "def square(n): return n * n",
      notes: "함수 이름은 역할을 드러내야 한다.",
    },
    {
      line: 2,
      code: "    return 1 if n == 0 else n * factorial(n - 1)",
      explanation: "n이 0이면 1, 아니면 n과 factorial(n-1)을 곱한다.",
      analogy: "인형 안에 더 작은 인형이 들어있는 러시안 인형과 같다.",
      alternativeExample: "return n * factorial(n - 1) if n else 1",
      notes: "재귀 종료 조건이 없으면 무한 재귀에 빠진다.",
    },
  ],
};

describe("Chapter4", () => {
  it("renders the chapter's title", () => {
    render(<Chapter4 content={content} />);

    expect(screen.getByText("Line-by-Line Explanation")).toBeInTheDocument();
  });

  it("renders each line's code, explanation, analogy, alternative example and notes", () => {
    render(<Chapter4 content={content} />);

    expect(screen.getByText("def factorial(n):")).toBeInTheDocument();
    expect(screen.getByText("factorial이라는 함수를 정의한다.")).toBeInTheDocument();
    expect(screen.getByText("요리 레시피 제목을 적는 것과 같다.")).toBeInTheDocument();
    expect(screen.getByText("def square(n): return n * n")).toBeInTheDocument();
    expect(screen.getByText("함수 이름은 역할을 드러내야 한다.")).toBeInTheDocument();
  });

  it("shows the line number for each explanation", () => {
    render(<Chapter4 content={content} />);

    expect(screen.getAllByTestId("chapter4-line-number").map((el) => el.textContent)).toEqual([
      "1",
      "2",
    ]);
  });

  it("renders every explanation in the list, not just the first", () => {
    render(<Chapter4 content={content} />);

    expect(
      screen.getByText("n이 0이면 1, 아니면 n과 factorial(n-1)을 곱한다."),
    ).toBeInTheDocument();
  });
});
