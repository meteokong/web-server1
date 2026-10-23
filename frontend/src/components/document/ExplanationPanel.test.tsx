import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import ExplanationPanel from "./ExplanationPanel";
import type { DocumentContent } from "@/types/document";

const content: DocumentContent = {
  chapter1: { title: "What This Code Does", summary: "배열을 정렬한다." },
  chapter2: {
    title: "Prerequisites Knowledge",
    concepts: [
      {
        name: "재귀함수",
        explanation: "자기 자신을 호출하는 함수",
        analogy: "러시안 인형",
        example: "f(n) = f(n-1)",
        useCases: "분할정복",
      },
    ],
  },
  chapter3: {
    title: "Code Structure Overview",
    flowchart: "main -> sort -> print",
    fileBreakdown: { "main.py": "엔트리 포인트" },
  },
  chapter4: {
    title: "Line-by-Line Explanation",
    explanations: [
      {
        line: 1,
        code: "def sort(arr):",
        explanation: "정렬 함수를 정의한다.",
        analogy: "요리 레시피",
        alternativeExample: "def noop(): pass",
        notes: "주의사항 없음",
      },
    ],
  },
  chapter5: {
    title: "Execution Flow Simulation",
    steps: [{ step: 1, description: "배열을 입력받는다." }],
  },
  chapter6: {
    title: "Core Concepts Summary",
    concepts: [
      {
        name: "재귀함수",
        whatItIs: "자기 호출",
        whyItsUsed: "반복을 간결하게 표현",
        whereItsApplied: "트리 순회",
      },
    ],
  },
  chapter7: {
    title: "Common Mistakes",
    mistakes: [
      {
        wrong: "종료 조건 없이 재귀",
        right: "종료 조건을 명시",
        why: "무한 재귀로 스택 오버플로우가 난다",
        fix: "base case 추가",
      },
    ],
  },
};

describe("ExplanationPanel", () => {
  it("renders a navigation item for each of the 7 chapters", () => {
    render(<ExplanationPanel content={content} />);

    expect(screen.getByRole("button", { name: /What This Code Does/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Prerequisites Knowledge/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Code Structure Overview/i })).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /Line-by-Line Explanation/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /Execution Flow Simulation/i }),
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Core Concepts Summary/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Common Mistakes/i })).toBeInTheDocument();
  });

  it("defaults to showing chapter1's content", () => {
    render(<ExplanationPanel content={content} />);

    expect(screen.getByText("배열을 정렬한다.")).toBeInTheDocument();
  });

  it("switches to chapter2's content (via the dedicated Chapter2 component) on nav click", async () => {
    const user = userEvent.setup();
    render(<ExplanationPanel content={content} />);

    await user.click(screen.getByRole("button", { name: /Prerequisites Knowledge/i }));

    expect(screen.getByText("재귀함수")).toBeInTheDocument();
    expect(screen.getByText("자기 자신을 호출하는 함수")).toBeInTheDocument();
  });

  it("switches to chapter4's content (via the dedicated Chapter4 component) on nav click", async () => {
    const user = userEvent.setup();
    render(<ExplanationPanel content={content} />);

    await user.click(screen.getByRole("button", { name: /Line-by-Line Explanation/i }));

    expect(screen.getByText("def sort(arr):")).toBeInTheDocument();
  });

  it("renders chapter3's structured fields (flowchart + file breakdown) generically", async () => {
    const user = userEvent.setup();
    render(<ExplanationPanel content={content} />);

    await user.click(screen.getByRole("button", { name: /Code Structure Overview/i }));

    expect(screen.getByText("main -> sort -> print")).toBeInTheDocument();
    expect(screen.getByText("main.py")).toBeInTheDocument();
    expect(screen.getByText("엔트리 포인트")).toBeInTheDocument();
  });

  it("renders chapter7's mistakes generically", async () => {
    const user = userEvent.setup();
    render(<ExplanationPanel content={content} />);

    await user.click(screen.getByRole("button", { name: /Common Mistakes/i }));

    expect(screen.getByText("종료 조건 없이 재귀")).toBeInTheDocument();
    expect(screen.getByText("종료 조건을 명시")).toBeInTheDocument();
  });
});
