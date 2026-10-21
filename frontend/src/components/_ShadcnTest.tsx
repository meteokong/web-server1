import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

// TEMPORARY manual-testing component for the T022 Tailwind + shadcn/ui setup.
// Not part of any tasks.md task — remove once a real feature uses these components.

export function ShadcnTest() {
  return (
    <div className="mt-4 max-w-sm space-y-3 rounded-lg border p-4">
      <h2 className="text-lg font-semibold">Tailwind + shadcn/ui 테스트</h2>
      <Input placeholder="이메일을 입력하세요" />
      <div className="flex gap-2">
        <Button>기본 버튼</Button>
        <Button variant="outline">아웃라인</Button>
        <Button variant="destructive">삭제</Button>
      </div>
    </div>
  );
}
