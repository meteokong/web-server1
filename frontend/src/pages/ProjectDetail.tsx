import { useId, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { deleteProject, getProject, updateProject } from "@/services/project-service";

/**
 * ProjectDetail: fetches and shows one project by the :projectId route
 * param. The task timeline (listing/managing the project's tasks) is a
 * later feature (Phase 6+) — this renders a placeholder for it so the
 * page's layout is in place before that work lands.
 *
 * Also offers the minimal inline edit (title only) and delete (soft
 * delete, then back to the dashboard) actions needed for the T059/T060
 * manual browser tests — project-service.ts already had updateProject/
 * deleteProject (T053) but nothing in the UI called them yet.
 */
export default function ProjectDetail() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const titleInputId = useId();
  const [isEditing, setIsEditing] = useState(false);
  const [titleInput, setTitleInput] = useState("");

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

  const updateMutation = useMutation({
    mutationFn: (title: string) => updateProject(projectId as string, { title }),
    onSuccess: (updated) => {
      queryClient.setQueryData(["projects", projectId], updated);
      // exact: true — a plain invalidateQueries({queryKey: ["projects"]})
      // prefix-matches this very query (["projects", projectId]) too and
      // would refetch it, clobbering the setQueryData above with
      // whatever the (now stale) list-query cache returns.
      queryClient.invalidateQueries({ queryKey: ["projects"], exact: true });
      setIsEditing(false);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => deleteProject(projectId as string),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"], exact: true });
      navigate("/");
    },
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
      {isEditing ? (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            updateMutation.mutate(titleInput);
          }}
        >
          <label htmlFor={titleInputId}>제목</label>
          <Input
            id={titleInputId}
            value={titleInput}
            onChange={(e) => setTitleInput(e.target.value)}
          />
          <Button type="submit" disabled={updateMutation.isPending}>
            저장
          </Button>
          <Button type="button" onClick={() => setIsEditing(false)}>
            취소
          </Button>
        </form>
      ) : (
        <h1>{project.title}</h1>
      )}
      <p>{project.description ?? "설명이 없습니다."}</p>

      {!isEditing && (
        <Button
          onClick={() => {
            setTitleInput(project.title);
            setIsEditing(true);
          }}
        >
          제목 수정
        </Button>
      )}
      <Button onClick={() => deleteMutation.mutate()} disabled={deleteMutation.isPending}>
        삭제
      </Button>

      <section>
        <h2>태스크 타임라인</h2>
        <p>태스크 타임라인 기능은 아직 구현되지 않았습니다.</p>
      </section>
    </div>
  );
}
