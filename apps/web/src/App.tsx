import { useCallback } from "react";
import ReviewPage from "./pages/ReviewPage";
import { DEMO } from "./api/client";

const DEMO_OPTIONS = [
  {
    projectId: DEMO.projectId,
    chapterId: DEMO.chapterId,
    label: "示例有声书 · 第一章",
  },
];

function navigateToChapter(projectId: string, chapterId: string) {
  const url = new URL(window.location.href);
  url.searchParams.set("project_id", projectId);
  url.searchParams.set("chapter_id", chapterId);
  window.location.href = url.toString();
}

/** 应用根组件 — Review 页 + 最小项目导航 */
export default function App() {
  const params = new URLSearchParams(window.location.search);
  const projectId = params.get("project_id") || DEMO.projectId;
  const chapterId = params.get("chapter_id") || DEMO.chapterId;

  const onProjectChange = useCallback((e: React.ChangeEvent<HTMLSelectElement>) => {
    navigateToChapter(e.target.value, chapterId);
  }, [chapterId]);

  const onChapterChange = useCallback((e: React.ChangeEvent<HTMLSelectElement>) => {
    navigateToChapter(projectId, e.target.value);
  }, [projectId]);

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-top">
          <div className="header-brand">
            <h1>audiobook-cleaner-lab</h1>
            <span className="badge">Review</span>
          </div>
          <p className="header-subtitle">
            中文有声书录音 → ASR / 对齐 / LLM 机切建议 → 人工审核 → FFmpeg 导出
          </p>
        </div>
        <nav className="project-nav" aria-label="项目与章节">
          <label className="nav-field">
            <span>项目</span>
            <select value={projectId} onChange={onProjectChange}>
              <option value={DEMO.projectId}>book_001 · 示例有声书</option>
            </select>
          </label>
          <label className="nav-field">
            <span>章节</span>
            <select value={chapterId} onChange={onChapterChange}>
              <option value={DEMO.chapterId}>chapter_001 · 第一章</option>
            </select>
          </label>
          <button
            type="button"
            className="btn nav-demo"
            onClick={() => navigateToChapter(DEMO.projectId, DEMO.chapterId)}
          >
            打开演示章节
          </button>
        </nav>
        <ol className="step-bar">
          <li className="step done">导入</li>
          <li className="step done">ASR / 对齐</li>
          <li className="step active">Review</li>
          <li className="step">导出</li>
        </ol>
      </header>
      <ReviewPage
        projectId={projectId}
        chapterId={chapterId}
        demoOptions={DEMO_OPTIONS}
        onOpenDemo={() => navigateToChapter(DEMO.projectId, DEMO.chapterId)}
      />
    </div>
  );
}
