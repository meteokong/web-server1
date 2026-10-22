import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import Chapter2 from "./Chapter2";
import type { Chapter2Content } from "@/types/document";

const content: Chapter2Content = {
  title: "Prerequisites Knowledge",
  concepts: [
    {
      name: "재귀함수",
      explanation: "자기 자신을 호출하는 함수",
      analogy: "러시안 인형처럼 안에 자기와 똑같은 작은 인형이 들어있는 것",
      example: "factorial(n) = n * factorial(n-1)",
      useCases: "트리 순회, 분할정복 알고리즘",
    },
    {
      name: "배열",
      explanation: "같은 타입의 값을 순서대로 저장하는 자료구조",
      analogy: "줄지어 늘어선 사물함",
      example: "const arr = [1, 2, 3];",
      useCases: "정렬, 검색",
    },
  ],
};

describe("Chapter2", () => {
  it("renders the chapter's title", () => {
    render(<Chapter2 content={content} />);

    expect(screen.getByText("Prerequisites Knowledge")).toBeInTheDocument();
  });

  it("renders a card per concept with name/explanation/analogy/example/useCases", () => {
    render(<Chapter2 content={content} />);

    expect(screen.getByText("재귀함수")).toBeInTheDocument();
    expect(screen.getByText("자기 자신을 호출하는 함수")).toBeInTheDocument();
    expect(
      screen.getByText("러시안 인형처럼 안에 자기와 똑같은 작은 인형이 들어있는 것"),
    ).toBeInTheDocument();
    expect(screen.getByText("factorial(n) = n * factorial(n-1)")).toBeInTheDocument();
    expect(screen.getByText("트리 순회, 분할정복 알고리즘")).toBeInTheDocument();
  });

  it("renders every concept in the list, not just the first", () => {
    render(<Chapter2 content={content} />);

    expect(screen.getByText("배열")).toBeInTheDocument();
    expect(screen.getByText("줄지어 늘어선 사물함")).toBeInTheDocument();
  });
});
