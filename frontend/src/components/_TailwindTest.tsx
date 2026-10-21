import { Button } from "@/components/ui/button";

// TEMPORARY manual-testing component for Tailwind CSS + shadcn/ui (T022).
// Not part of any tasks.md task — remove once a real feature exercises these.

const TAILWIND_CLASS_EXPLANATIONS = [
  { className: "bg-blue-500", description: "배경색을 파란색(blue, 색상 단계 500)으로 지정" },
  { className: "text-white", description: "글자 색을 흰색으로 지정" },
  { className: "p-4", description: "안쪽 여백(padding)을 사방 1rem(16px)으로 지정" },
  { className: "rounded-lg", description: "모서리를 크게(large) 둥글게 처리" },
];

function TailwindClassSection() {
  return (
    <section className="mt-4 max-w-sm rounded-lg border p-4">
      <h2 className="mb-2 text-lg font-semibold">Tailwind 클래스 테스트</h2>

      <div className="rounded-lg bg-blue-500 p-4 text-white">
        bg-blue-500 text-white p-4 rounded-lg 적용된 박스
      </div>

      <ul className="mt-3 space-y-1 text-sm">
        {TAILWIND_CLASS_EXPLANATIONS.map(({ className, description }) => (
          <li key={className}>
            <code className="rounded bg-muted px-1 py-0.5">{className}</code> — {description}
          </li>
        ))}
      </ul>
    </section>
  );
}

function ShadcnButtonSection() {
  function handleClick(variant: string) {
    alert(variant);
  }

  return (
    <section className="mt-4 max-w-sm rounded-lg border p-4">
      <h2 className="mb-2 text-lg font-semibold">shadcn/ui 버튼 테스트</h2>
      <div className="flex gap-2">
        <Button variant="default" onClick={() => handleClick("default")}>
          default
        </Button>
        <Button variant="outline" onClick={() => handleClick("outline")}>
          outline
        </Button>
        <Button variant="ghost" onClick={() => handleClick("ghost")}>
          ghost
        </Button>
      </div>
    </section>
  );
}

function ResponsiveGridSection() {
  const cards = [
    { title: "카드 1", body: "모바일: 1열, 태블릿(md): 2열, 데스크톱(lg): 3열" },
    { title: "카드 2", body: "브라우저 창 너비를 줄이거나 늘려서 확인하세요" },
    { title: "카드 3", body: "grid-cols-1 md:grid-cols-2 lg:grid-cols-3" },
  ];

  return (
    <section className="mt-4 max-w-3xl rounded-lg border p-4">
      <h2 className="mb-2 text-lg font-semibold">반응형 디자인 테스트</h2>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
        {cards.map((card) => (
          <div key={card.title} className="rounded-lg border bg-card p-4 text-card-foreground">
            <h3 className="font-medium">{card.title}</h3>
            <p className="mt-1 text-sm text-muted-foreground">{card.body}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

export function TailwindTest() {
  return (
    <div>
      <TailwindClassSection />
      <ShadcnButtonSection />
      <ResponsiveGridSection />
    </div>
  );
}
