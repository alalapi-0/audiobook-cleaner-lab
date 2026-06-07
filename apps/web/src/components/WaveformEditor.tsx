import { useEffect, useRef, useState } from "react";
import WaveSurfer from "wavesurfer.js";
import RegionsPlugin from "wavesurfer.js/dist/plugins/regions.esm.js";

export interface DeleteRange {
  range_id: string;
  start: number;
  end: number;
  reason?: string;
  source_segment_ids?: string[];
  confirmed_by_user?: boolean;
}

interface Props {
  audioUrl: string;
  deleteRanges: DeleteRange[];
  onRangesChange: (ranges: DeleteRange[]) => void;
  selectedSegmentStart?: number;
}

/** wavesurfer.js 波形编辑器 — 显示删除区间并支持拖动 */
export default function WaveformEditor({
  audioUrl,
  deleteRanges,
  onRangesChange,
  selectedSegmentStart,
}: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WaveSurfer | null>(null);
  const regionsRef = useRef<ReturnType<typeof RegionsPlugin.create> | null>(null);
  const [ready, setReady] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    let cancelled = false;
    setReady(false);
    setError(null);

    const ws = WaveSurfer.create({
      container: containerRef.current,
      waveColor: "#90caf9",
      progressColor: "#1565c0",
      height: 80,
      url: audioUrl,
      interact: true,
    });

    const regions = ws.registerPlugin(RegionsPlugin.create());
    wsRef.current = ws;
    regionsRef.current = regions;

    ws.on("ready", () => {
      if (cancelled) return;
      setReady(true);
      deleteRanges.forEach((dr, i) => {
        regions.addRegion({
          id: dr.range_id || `del_${i}`,
          start: dr.start,
          end: dr.end,
          color: "rgba(229, 57, 53, 0.35)",
          drag: true,
          resize: true,
        });
      });
    });

    ws.on("error", (err) => {
      if (!cancelled) setError(String(err));
    });

    regions.on("region-updated", () => {
      const updated: DeleteRange[] = regions
        .getRegions()
        .map((r, i) => ({
          range_id: r.id || `del_${i + 1}`,
          start: r.start,
          end: r.end,
          reason: "user_adjusted",
          confirmed_by_user: true,
        }));
      onRangesChange(updated);
    });

    return () => {
      cancelled = true;
      setReady(false);
      ws.destroy();
      wsRef.current = null;
      regionsRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [audioUrl]);

  const playAround = (center: number, windowSec = 2) => {
    const ws = wsRef.current;
    if (!ws || !ready) return;
    try {
      const dur = ws.getDuration();
      if (!dur || dur <= 0) return;
      const start = Math.max(0, center - windowSec);
      const end = Math.min(dur, center + windowSec);
      ws.play(start, end);
    } catch {
      // StrictMode 重挂载时可能短暂未就绪，忽略即可
    }
  };

  return (
    <div className="waveform-editor">
      <div className="waveform-toolbar">
        <button
          type="button"
          className="btn"
          disabled={!ready}
          onClick={() => {
            if (ready) wsRef.current?.playPause();
          }}
        >
          播放/暂停
        </button>
        {selectedSegmentStart != null && (
          <button
            type="button"
            className="btn"
            disabled={!ready}
            onClick={() => playAround(selectedSegmentStart)}
          >
            播放切点前后 2 秒
          </button>
        )}
        <span className="waveform-legend">
          <span className="legend-delete">■ 删除区间（可拖动）</span>
        </span>
      </div>
      <div ref={containerRef} className="waveform-container" />
      {error && (
        <p className="status error">
          波形加载失败，请刷新页面或检查音频文件是否可访问。
        </p>
      )}
      {!ready && !error && <p className="status">波形加载中…</p>}
    </div>
  );
}
