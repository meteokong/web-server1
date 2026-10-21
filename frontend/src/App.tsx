import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AuthStoreTest } from "./components/_AuthStoreTest";
import { DevTest } from "./components/_DevTest";
import { QueryTest } from "./components/_QueryTest";
import { ShadcnTest } from "./components/_ShadcnTest";
import { TailwindTest } from "./components/_TailwindTest";

/**
 * Stand-in for a page component that hasn't been built yet. Each route
 * below is replaced with its real page as that page's task is completed
 * (Login/Register: T035-T036, Dashboard: T054, ProjectDetail: T055,
 * TaskDetail: T083, Trash: T181).
 */
function PagePlaceholder({ label }: { label: string }) {
  return <div>{label} 페이지 (구현 예정)</div>;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<PagePlaceholder label="로그인" />} />
        <Route path="/register" element={<PagePlaceholder label="회원가입" />} />
        <Route path="/" element={<PagePlaceholder label="대시보드" />} />
        <Route path="/projects/:projectId" element={<PagePlaceholder label="프로젝트 상세" />} />
        <Route
          path="/projects/:projectId/tasks/:taskId"
          element={<PagePlaceholder label="태스크 상세" />}
        />
        <Route path="/trash" element={<PagePlaceholder label="휴지통" />} />
        {/* TEMPORARY: T019 TanStack Query manual test route, see _QueryTest.tsx */}
        <Route path="/query-test" element={<QueryTest />} />
        {/* TEMPORARY: T020 axios client + T021 Zustand store manual test route */}
        <Route
          path="/dev-test"
          element={
            <>
              <DevTest />
              <AuthStoreTest />
              <ShadcnTest />
              <TailwindTest />
            </>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
