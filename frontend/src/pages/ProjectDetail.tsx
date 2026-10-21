import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { getProject } from "@/services/project-service";

/**
 * ProjectDetail: fetches and shows one project by the :projectId route
 * param. The task timeline (listing/managing the project's tasks) is a
 * later feature (Phase 6+) — this renders a placeholder for it so the
 * page's layout is in place before that work lands.
 */
export default function ProjectDetail() {
  const { projectId } = useParams<{ projectId: string }>();
  const {
    data: project,
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ["projects", projectId],
    queryFn: () => getProject(projectId as string),
    enabled: Boolean(projectId),
  });

  if (isLoading) {
    return <p>로딩 중...</p>;
  }

  if (isError) {
    return <p role="alert">{error instanceof Error ? error.message : "오류가 발생했습니다."}</p>;
  }

  if (!project) {
    return null;
  }

  return (
    <div>
      <h1>{project.title}</h1>
      <p>{project.description ?? "설명이 없습니다."}</p>
      <section>
        <h2>태스크 타임라인</h2>
        <p>태스크 타임라인 기능은 아직 구현되지 않았습니다.</p>
      </section>
    </div>
  );
}
