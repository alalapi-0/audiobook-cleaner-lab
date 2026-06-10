import { DEMO } from "../api/client";

const ROUTE_LABELS: Record<string, { title: string; desc: string }> = {
  "/admin": {
    title: "管理后台",
    desc: "批处理队列、项目进度总览等功能尚在规划中，当前请使用 CLI（batch_process.py）与 Review 页完成主链路。",
  },
  "/workbench": {
    title: "审核工作台",
    desc: "多章节并排审核工作台尚在规划中。当前请在 Review 页逐章审核并保存 cut_plan。",
  },
  "/preview": {
    title: "导出预览",
    desc: "导出结果在线预览尚在规划中。请先保存 Review，再运行 run_export.py --dry-run 查看导出计划。",
  },
};

interface Props {
  path: string;
  onGoReview: () => void;
}

/** 规划中路由说明页 */
export default function PlannedPage({ path, onGoReview }: Props) {
  const info = ROUTE_LABELS[path] ?? {
    title: "功能规划中",
    desc: "该页面尚未实现，请返回 Review 继续审核。",
  };

  return (
    <main className="planned-page">
      <div className="planned-card">
        <span className="planned-badge">规划中</span>
        <h2>{info.title}</h2>
        <p>{info.desc}</p>
        <div className="planned-actions">
          <button type="button" className="btn primary" onClick={onGoReview}>
            返回 Review（{DEMO.projectId}/{DEMO.chapterId}）
          </button>
          <a className="btn" href="/">
            回到首页
          </a>
        </div>
      </div>
    </main>
  );
}
