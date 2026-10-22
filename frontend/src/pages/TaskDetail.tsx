import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Tabs } from "radix-ui";
import { getTask } from "@/services/task-service";

const PLACEHOLDER_TEXT = "아직 구현되지 않았습니다.";

/**
 * TaskDetail: fetches and shows one task by the :taskId route param, with
 * Document/Practice/Q&A tabs (radix Tabs). Each tab's real content
 * (document generation, practice problems, Q&A chat) is a later feature —
 * this renders a placeholder per tab so the page's layout/navigation is in
 * place before that work lands.
 */
export default function TaskDetail() {
  const { taskId } = useParams<{ taskId: string }>();

  const {
    data: task,
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ["tasks", "detail", taskId],
    queryFn: () => getTask(taskId as string),
    enabled: Boolean(taskId),
  });

  if (isLoading) {
    return <p>로딩 중...</p>;
  }

  if (isError) {
    return <p role="alert">{error instanceof Error ? error.message : "오류가 발생했습니다."}</p>;
  }

  if (!task) {
    return null;
  }

  return (
    <div>
      <h1>{task.title}</h1>
      <p>{task.description ?? "설명이 없습니다."}</p>

      <Tabs.Root defaultValue="document">
        <Tabs.List>
          <Tabs.Trigger value="document">문서</Tabs.Trigger>
          <Tabs.Trigger value="practice">연습</Tabs.Trigger>
          <Tabs.Trigger value="qa">질의응답</Tabs.Trigger>
        </Tabs.List>
        <Tabs.Content value="document">
          <p>{PLACEHOLDER_TEXT}</p>
        </Tabs.Content>
        <Tabs.Content value="practice">
          <p>{PLACEHOLDER_TEXT}</p>
        </Tabs.Content>
        <Tabs.Content value="qa">
          <p>{PLACEHOLDER_TEXT}</p>
        </Tabs.Content>
      </Tabs.Root>
    </div>
  );
}
