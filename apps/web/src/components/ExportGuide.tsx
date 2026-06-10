import { useState } from "react";

interface Props {
  projectId: string;
  chapterId: string;
  compact?: boolean;
}

/** 导出引导：显示 CLI 命令并支持复制 */
export default function ExportGuide({ projectId, chapterId, compact = false }: Props) {
  const [copied, setCopied] = useState(false);
  const dryRunCmd = `.venv/bin/python scripts/run_export.py --project-id ${projectId} --chapter-id ${chapterId} --dry-run`;
  const exportCmd = `.venv/bin/python scripts/run_export.py --project-id ${projectId} --chapter-id ${chapterId}`;

  const copy = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setCopied(false);
    }
  };

  if (compact) {
    return (
      <div className="export-guide compact">
        <button type="button" className="btn primary" onClick={() => copy(dryRunCmd)}>
          {copied ? "已复制 dry-run 命令" : "复制导出 dry-run 命令"}
        </button>
      </div>
    );
  }

  return (
    <section className="export-guide">
      <h2>导出音频（CLI）</h2>
      <p>Review 与波形微调保存后，在仓库根目录执行：</p>
      <p className="export-label">1. 先 dry-run 预览删除区间：</p>
      <code className="export-cmd">{dryRunCmd}</code>
      <button type="button" className="btn" onClick={() => copy(dryRunCmd)}>
        复制 dry-run
      </button>
      <p className="export-label">2. 确认无误后正式导出：</p>
      <code className="export-cmd">{exportCmd}</code>
      <button type="button" className="btn" onClick={() => copy(exportCmd)}>
        复制导出命令
      </button>
      {copied && <p className="copy-hint">已复制到剪贴板</p>}
    </section>
  );
}
