import { useCallback, useEffect, useState } from "react";
import {
  audioServeUrl,
  fetchCutPlan,
  fetchReviewData,
  saveReview,
  updateCutPlan,
  type CutPlan,
  type ReviewData,
  type ReviewSegment,
  type UserDecision,
} from "../api/client";
import WaveformEditor, { type DeleteRange } from "../components/WaveformEditor";

interface DemoOption {
  projectId: string;
  chapterId: string;
  label: string;
}

interface Props {
  projectId: string;
  chapterId: string;
  demoOptions?: DemoOption[];
  onOpenDemo?: () => void;
}

type UserAction = "keep" | "delete" | "uncertain";

/** Review 三栏 MVP 页面 */
export default function ReviewPage({
  projectId,
  chapterId,
  onOpenDemo,
}: Props) {
  const [data, setData] = useState<ReviewData | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [userActions, setUserActions] = useState<Record<string, UserAction>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saveMsg, setSaveMsg] = useState<string | null>(null);
  const [cutPlan, setCutPlan] = useState<CutPlan | null>(null);
  const [deleteRanges, setDeleteRanges] = useState<DeleteRange[]>([]);

  const loadCutPlan = useCallback(async () => {
    try {
      const cp = await fetchCutPlan(projectId, chapterId);
      if (!cp) {
        return false;
      }
      setCutPlan(cp);
      setDeleteRanges(cp.delete_ranges ?? []);
      return true;
    } catch {
      setCutPlan(null);
      setDeleteRanges([]);
      return false;
    }
  }, [projectId, chapterId]);

  const buildInitialDeleteRanges = useCallback((segments: ReviewSegment[]): DeleteRange[] => {
    return segments
      .filter((s) => s.model_action === "delete" && s.suggested_cut)
      .map((s, index) => {
        const cut = s.suggested_cut!;
        const pre = cut.pre_padding ?? 0.08;
        const post = cut.post_padding ?? 0.12;
        return {
          range_id: `del_${String(index + 1).padStart(3, "0")}`,
          start: Math.max(0, cut.start - pre),
          end: cut.end + post,
          reason: s.model_reason,
          confirmed_by_user: false,
        };
      });
  }, []);

  useEffect(() => {
    setLoading(true);
    setError(null);
    setSaveMsg(null);
    fetchReviewData(projectId, chapterId)
      .then((d) => {
        setData(d);
        const initial: Record<string, UserAction> = {};
        d.segments.forEach((s) => {
          const ma = s.model_action;
          initial[s.segment_id] =
            ma === "delete" || ma === "keep" || ma === "uncertain" ? ma : "uncertain";
        });
        setUserActions(initial);
        if (d.segments.length > 0) {
          setSelectedId(d.segments[0].segment_id);
        }
        setDeleteRanges(buildInitialDeleteRanges(d.segments));
      })
      .catch((e) => setError(e instanceof Error ? e.message : String(e)))
      .finally(() => setLoading(false));
  }, [projectId, chapterId, buildInitialDeleteRanges]);

  const selected: ReviewSegment | undefined = data?.segments.find(
    (s) => s.segment_id === selectedId,
  );

  const setAction = useCallback((segId: string, action: UserAction) => {
    setUserActions((prev) => ({ ...prev, [segId]: action }));
  }, []);

  const handleSave = async () => {
    if (!data) return;
    const decisions: UserDecision[] = data.segments.map((s) => ({
      segment_id: s.segment_id,
      user_action: userActions[s.segment_id] ?? "uncertain",
      user_adjusted_cut: s.suggested_cut ?? undefined,
    }));
    try {
      const result = await saveReview(projectId, chapterId, decisions);
      setSaveMsg(
        `已保存 cut_plan（delete: ${result.delete_count}, keep: ${result.keep_count}）`,
      );
      await loadCutPlan();
    } catch (e) {
      setSaveMsg(`保存失败: ${e instanceof Error ? e.message : String(e)}`);
    }
  };

  const handleSaveCutPlan = async () => {
    try {
      await updateCutPlan(projectId, chapterId, {
        delete_ranges: deleteRanges,
        keep_ranges: cutPlan?.keep_ranges ?? [],
      });
      setSaveMsg("cut_plan 已更新（波形微调）");
    } catch (e) {
      setSaveMsg(`cut_plan 保存失败: ${e instanceof Error ? e.message : String(e)}`);
    }
  };

  const exportCmd = `.venv/bin/python scripts/run_export.py --project-id ${projectId} --chapter-id ${chapterId} --dry-run`;

  if (loading) return <p className="status page-status">加载中…</p>;

  if (error) {
    return (
      <div className="error-panel">
        <h2>无法加载章节</h2>
        <p>{error}</p>
        <p className="error-hint">请检查 URL 中的 project_id 与 chapter_id，或打开演示章节继续体验。</p>
        {onOpenDemo && (
          <button type="button" className="btn primary" onClick={onOpenDemo}>
            打开演示章节 book_001 / chapter_001
          </button>
        )}
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="review-page">
      <div className="review-intro">
        <p>
          当前章节：<strong>{data.title}</strong>（{projectId} / {chapterId}）· 共{" "}
          <strong>{data.segments.length}</strong> 个 segment。请逐条确认模型建议，保存后可用 CLI 导出。
        </p>
      </div>

      <div className="review-toolbar">
        <span className="toolbar-meta">
          engine: {data.llm_engine ?? "mock"}
        </span>
        <button type="button" className="btn primary save-btn" onClick={handleSave}>
          保存 Review &amp; cut_plan
        </button>
        {saveMsg && <span className="save-msg">{saveMsg}</span>}
      </div>

      {saveMsg && saveMsg.startsWith("已保存") && (
        <aside className="export-hint">
          <strong>下一步：导出音频</strong>
          <p>Review 保存成功后，在仓库根目录运行：</p>
          <code className="export-cmd">{exportCmd}</code>
        </aside>
      )}

      <div className="review-columns">
        <section className="column source-column">
          <h2>原文</h2>
          <div className="text-block">{data.normalized_source_text}</div>
          {selected?.source_text && (
            <div className="highlight-box">
              <strong>当前对齐:</strong> {selected.source_text}
            </div>
          )}
        </section>

        <section className="column asr-column">
          <h2>ASR Segments</h2>
          <ul className="segment-list">
            {data.segments.map((seg) => (
              <li
                key={seg.segment_id}
                className={`segment-item ${seg.segment_id === selectedId ? "active" : ""} status-${seg.alignment_status}`}
                onClick={() => setSelectedId(seg.segment_id)}
              >
                <span className="seg-id">{seg.segment_id}</span>
                <span className="seg-time">
                  {seg.start?.toFixed(2)}s – {seg.end?.toFixed(2)}s
                </span>
                <span className="seg-text">{seg.asr_text}</span>
                <span className={`status-tag ${seg.alignment_status}`}>
                  {seg.alignment_status}
                </span>
              </li>
            ))}
          </ul>
        </section>

        <section className="column decision-column">
          <h2>模型建议 &amp; 人工确认</h2>
          {selected ? (
            <div className="decision-panel">
              <p>
                <strong>模型:</strong> {selected.model_action}{" "}
                <span className="confidence">
                  ({((selected.model_confidence ?? 0) * 100).toFixed(0)}%)
                </span>
              </p>
              <p className="reason">{selected.model_reason}</p>
              {selected.model_action === "uncertain" && (
                <p className="warn">⚠ 需人工试听确认</p>
              )}
              <div className="action-buttons">
                <button
                  type="button"
                  className={`btn ${userActions[selected.segment_id] === "keep" ? "active-keep" : ""}`}
                  onClick={() => setAction(selected.segment_id, "keep")}
                >
                  确认保留
                </button>
                <button
                  type="button"
                  className={`btn ${userActions[selected.segment_id] === "delete" ? "active-delete" : ""}`}
                  onClick={() => setAction(selected.segment_id, "delete")}
                >
                  确认删除
                </button>
                <button
                  type="button"
                  className={`btn ${userActions[selected.segment_id] === "uncertain" ? "active-uncertain" : ""}`}
                  onClick={() => setAction(selected.segment_id, "uncertain")}
                >
                  不确定
                </button>
              </div>
            </div>
          ) : (
            <p>请选择 segment</p>
          )}

          <h3>全部决策摘要</h3>
          <ul className="summary-list">
            {data.segments.map((s) => (
              <li key={s.segment_id}>
                {s.segment_id}: 模型 {s.model_action} → 用户{" "}
                <strong>{userActions[s.segment_id]}</strong>
              </li>
            ))}
          </ul>
        </section>
      </div>

      <footer className="review-footer waveform-section">
        <h2 className="waveform-title">波形微调</h2>
        <WaveformEditor
          audioUrl={audioServeUrl(data.source_audio)}
          deleteRanges={deleteRanges}
          onRangesChange={setDeleteRanges}
          selectedSegmentStart={selected?.start}
        />
        <div className="waveform-actions">
          <button type="button" className="btn primary" onClick={handleSaveCutPlan}>
            保存波形 cut_plan 微调
          </button>
        </div>
      </footer>
    </div>
  );
}
