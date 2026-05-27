import { useCallback, useEffect, useState } from "react";
import {
  fetchReviewData,
  saveReview,
  type ReviewData,
  type ReviewSegment,
  type UserDecision,
} from "../api/client";

interface Props {
  projectId: string;
  chapterId: string;
}

type UserAction = "keep" | "delete" | "uncertain";

/** Review 三栏 MVP 页面 */
export default function ReviewPage({ projectId, chapterId }: Props) {
  const [data, setData] = useState<ReviewData | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [userActions, setUserActions] = useState<Record<string, UserAction>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saveMsg, setSaveMsg] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
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
      })
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  }, [projectId, chapterId]);

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
    } catch (e) {
      setSaveMsg(`保存失败: ${e}`);
    }
  };

  if (loading) return <p className="status">加载中…</p>;
  if (error) return <p className="status error">加载失败: {error}</p>;
  if (!data) return null;

  return (
    <div className="review-page">
      <div className="review-toolbar">
        <span>
          {data.title} · {data.segments.length} segments · engine: {data.llm_engine}
        </span>
        <button type="button" className="btn primary" onClick={handleSave}>
          保存 Review &amp; cut_plan
        </button>
        {saveMsg && <span className="save-msg">{saveMsg}</span>}
      </div>

      <div className="review-columns">
        {/* 原文区 */}
        <section className="column source-column">
          <h2>原文</h2>
          <div className="text-block">{data.normalized_source_text}</div>
          {selected?.source_text && (
            <div className="highlight-box">
              <strong>当前对齐:</strong> {selected.source_text}
            </div>
          )}
        </section>

        {/* ASR 区 */}
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

        {/* 模型建议区 */}
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

      <footer className="review-footer">
        <span>音频: {data.source_audio}</span>
        <span>选中: {selectedId ?? "—"}</span>
      </footer>
    </div>
  );
}
