interface Props {
  path: string;
  onGoReview: () => void;
}

/** 未知路由 404 说明页 */
export default function NotFoundPage({ path, onGoReview }: Props) {
  return (
    <main className="planned-page">
      <div className="planned-card not-found">
        <span className="planned-badge">404</span>
        <h2>页面不存在</h2>
        <p>
          路径 <code>{path}</code> 未实现。本工具当前以 Review 页为核心，请返回演示章节继续。
        </p>
        <div className="planned-actions">
          <button type="button" className="btn primary" onClick={onGoReview}>
            打开演示章节
          </button>
          <a className="btn" href="/">
            回到首页
          </a>
        </div>
      </div>
    </main>
  );
}
