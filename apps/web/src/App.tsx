import { useCallback, useMemo, useState } from "react";
import ReviewPage from "./pages/ReviewPage";
import PlannedPage from "./pages/PlannedPage";
import NotFoundPage from "./pages/NotFoundPage";
import ImportGuide from "./components/ImportGuide";
import ExportGuide from "./components/ExportGuide";
import { DEMO } from "./api/client";

const PLANNED_PATHS = new Set(["/admin", "/workbench", "/preview"]);

function navigateToChapter(projectId: string, chapterId: string) {
  const url = new URL(window.location.href);
  url.pathname = "/";
  url.searchParams.set("project_id", projectId);
  url.searchParams.set("chapter_id", chapterId);
  window.location.href = url.toString();
}

function normalizePathname(): string {
  const path = window.location.pathname.replace(/\/+$/, "") || "/";
  return path;
}

/** 应用根组件 — Review 页 + 最小项目导航 + 规划路由 */
export default function App() {
  const pathname = useMemo(normalizePathname, []);
  const params = new URLSearchParams(window.location.search);
  const projectId = params.get("project_id") || DEMO.projectId;
  const chapterId = params.get("chapter_id") || DEMO.chapterId;
  const [showExport, setShowExport] = useState(false);

  const onProjectChange = useCallback((e: React.ChangeEvent<HTMLSelectElement>) => {
    navigateToChapter(e.target.value, chapterId);
  }, [chapterId]);

  const onChapterChange = useCallback((e: React.ChangeEvent<HTMLSelectElement>) => {
    navigateToChapter(projectId, e.target.value);
  }, [projectId]);

  const goReview = useCallback(() => {
    navigateToChapter(DEMO.projectId, DEMO.chapterId);
  }, []);

  const isReviewHome = pathname === "/" || pathname === "/review";
  const isPlanned = PLANNED_PATHS.has(pathname);
  const isUnknown = !isReviewHome && !isPlanned;

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
            <select value={projectId} onChange={onProjectChange} disabled={!isReviewHome}>
              <option value={DEMO.projectId}>book_001 · 示例有声书</option>
            </select>
          </label>
          <label className="nav-field">
            <span>章节</span>
            <select value={chapterId} onChange={onChapterChange} disabled={!isReviewHome}>
              <option value={DEMO.chapterId}>chapter_001 · 第一章</option>
            </select>
          </label>
          <button type="button" className="btn nav-demo" onClick={goReview}>
            打开演示章节
          </button>
        </nav>
        <ol className="step-bar">
          <li className="step done">导入</li>
          <li className="step done">ASR / 对齐</li>
          <li className={`step ${isReviewHome ? "active" : "done"}`}>Review</li>
          <li className={`step ${showExport ? "active" : ""}`}>
            <button
              type="button"
              className="step-link"
              onClick={() => setShowExport((v) => !v)}
            >
              导出
            </button>
          </li>
        </ol>
      </header>

      {showExport && isReviewHome && (
        <div className="page-section">
          <ExportGuide projectId={projectId} chapterId={chapterId} />
        </div>
      )}

      {isPlanned && <PlannedPage path={pathname} onGoReview={goReview} />}
      {isUnknown && <NotFoundPage path={pathname} onGoReview={goReview} />}
      {isReviewHome && (
        <>
          <div className="page-section">
            <ImportGuide />
          </div>
          <ReviewPage
            projectId={projectId}
            chapterId={chapterId}
            onOpenDemo={goReview}
            showInlineExport={!showExport}
          />
        </>
      )}
    </div>
  );
}
