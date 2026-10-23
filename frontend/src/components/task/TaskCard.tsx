import { Link } from "react-router-dom";
import type { Task } from "@/types/task";

export interface TaskCardProps {
  task: Task;
}

/**
 * Presentational card for one task, used by ProjectDetail's task timeline
 * (T082). Mirrors ProjectCard (T051) — no data fetching, just renders and
 * links through to TaskDetail (T083).
 */
export function TaskCard({ task }: TaskCardProps) {
  return (
    <article>
      <h3>
        <Link to={`/projects/${task.projectId}/tasks/${task.id}`}>{task.title}</Link>
      </h3>
      <p>Task {task.taskNumber}</p>
    </article>
  );
}
