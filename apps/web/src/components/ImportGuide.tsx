/** 导入自有素材的 Web 内简要指引 */
export default function ImportGuide() {
  return (
    <aside className="import-guide">
      <h2>导入自己的有声书章节</h2>
      <p>将章节 wav 与原文 txt 放入 <code>data/</code> 后，在仓库根目录运行：</p>
      <ol className="import-steps">
        <li>
          <code>python3 scripts/import_manifest.py create-project --project-id 你的书ID --title &quot;书名&quot;</code>
        </li>
        <li>
          <code>python3 scripts/import_manifest.py add-chapter --project-id 你的书ID --chapter-id 章节ID --title &quot;章节名&quot; --audio data/raw_audio/... --text data/source_text/...</code>
        </li>
        <li>
          <code>python3 scripts/run_asr.py ... && run_normalize.py && run_align.py && run_llm_cut.py</code>
        </li>
        <li>完成后用 URL 参数 <code>?project_id=...&amp;chapter_id=...</code> 打开 Review，或扩展顶部项目下拉（当前仅演示项目）。</li>
      </ol>
      <p className="import-note">详细步骤见仓库 <code>README.md</code>「Mock 单章全流程」。</p>
    </aside>
  );
}
