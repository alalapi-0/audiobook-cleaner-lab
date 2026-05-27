import ReviewPage from "./pages/ReviewPage";

/** 应用根组件 — Round 06 MVP 仅 Review 页 */
export default function App() {
  const params = new URLSearchParams(window.location.search);
  const projectId = params.get("project_id") || "book_001";
  const chapterId = params.get("chapter_id") || "chapter_001";

  return (
    <div className="app">
      <header className="app-header">
        <h1>audiobook-cleaner-lab Review</h1>
        <span className="badge">MVP</span>
      </header>
      <ReviewPage projectId={projectId} chapterId={chapterId} />
    </div>
  );
}
