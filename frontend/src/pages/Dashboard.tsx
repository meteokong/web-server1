import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { ProjectCard } from "@/components/project/ProjectCard";
import {
  CreateProjectModal,
  type CreateProjectModalValues,
} from "@/components/project/CreateProjectModal";
import { createProject, listProjects } from "@/services/project-service";

const PROJECTS_QUERY_KEY = ["projects"];

/**
 * Dashboard: lists the current user's active projects, and lets the user
 * create a new one via CreateProjectModal (T052) + project-service's
 * createProject (T053). A successful create invalidates the projects
 * query so the new project shows up immediately, without a manual
 * reload.
 */
export default function Dashboard() {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const queryClient = useQueryClient();
  const {
    data: projects,
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: PROJECTS_QUERY_KEY,
    queryFn: listProjects,
  });
  const createProjectMutation = useMutation({
    mutationFn: ({ title, description }: CreateProjectModalValues) =>
      createProject(title, description || null),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: PROJECTS_QUERY_KEY });
      setIsCreateModalOpen(false);
    },
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
        onSubmit={(values) => createProjectMutation.mutateAsync(values)}
      />
    </div>
  );
}
