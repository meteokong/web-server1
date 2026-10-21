import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { ProjectCard } from "@/components/project/ProjectCard";
import { CreateProjectModal } from "@/components/project/CreateProjectModal";
import { listProjects } from "@/services/project-service";

/**
 * Dashboard: lists the current user's active projects. Fetching is the
 * only concern here — the create-project flow (CreateProjectModal +
 * project-service.createProject, including refreshing this list after a
 * successful create) is wired in by T056.
 */
export default function Dashboard() {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const {
    data: projects,
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ["projects"],
    queryFn: listProjects,
  });

  return (
    <div>
      <h1>대시보드</h1>
      <Button onClick={() => setIsCreateModalOpen(true)}>새 프로젝트</Button>

      {isLoading && <p>로딩 중...</p>}
      {isError && <p role="alert">{error instanceof Error ? error.message : "오류가 발생했습니다."}</p>}
      {!isLoading && !isError && projects && projects.length === 0 && (
        <p>아직 프로젝트가 없습니다.</p>
      )}
      {!isLoading && !isError && projects && projects.length > 0 && (
        <div>
          {projects.map((project) => (
            <ProjectCard key={project.id} project={project} />
          ))}
        </div>
      )}

      <CreateProjectModal
        open={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSubmit={async () => {
          setIsCreateModalOpen(false);
        }}
      />
    </div>
  );
}
