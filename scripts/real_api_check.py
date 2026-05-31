#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""真实 LLM API 验证 — 生成样本、评估质量、写入 reports/real_api_runs/。"""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from packages.llm_core.adapters.openai_compatible import OpenAiCompatibleAdapter  # noqa: E402
from packages.llm_core.config import LlmApiConfig  # noqa: E402
from packages.llm_core.service import LlmCutService  # noqa: E402

# 三个独立测试场景（不依赖真实音频）
SAMPLE_PAYLOADS: list[dict[str, Any]] = [
    {
        "name": "matched_keep",
        "chapter_id": "real_api_sample_001",
        "segments": [
            {
                "segment_id": "seg_0001",
                "start": 0.0,
                "end": 3.5,
                "asr_text": "话说那日天色已晚",
                "alignment_status": "matched",
                "similarity": 0.94,
                "filler_candidates": [],
            },
            {
                "segment_id": "seg_0002",
                "start": 3.5,
                "end": 7.2,
                "asr_text": "他缓缓走进房间",
                "alignment_status": "matched",
                "similarity": 0.91,
                "filler_candidates": [],
            },
        ],
        "policy": {"never_auto_delete_below_confidence": 0.75, "require_user_for_uncertain": True},
        "expected": {"seg_0001": "keep", "seg_0002": "keep"},
    },
    {
        "name": "extra_and_restart",
        "chapter_id": "real_api_sample_002",
        "segments": [
            {
                "segment_id": "seg_0001",
                "start": 0.0,
                "end": 2.8,
                "asr_text": "嗯不对，我重新读",
                "alignment_status": "extra_candidate",
                "similarity": 0.12,
                "filler_candidates": [{"token": "嗯", "offset": 0}],
            },
            {
                "segment_id": "seg_0002",
                "start": 2.8,
                "end": 6.0,
                "asr_text": "话说那日天色已晚",
                "alignment_status": "matched",
                "similarity": 0.93,
                "filler_candidates": [],
            },
        ],
        "policy": {"never_auto_delete_below_confidence": 0.75, "require_user_for_uncertain": True},
        "expected": {"seg_0001": "delete", "seg_0002": "keep"},
    },
    {
        "name": "filler_uncertain",
        "chapter_id": "real_api_sample_003",
        "segments": [
            {
                "segment_id": "seg_0001",
                "start": 0.0,
                "end": 4.0,
                "asr_text": "那个，话说",
                "alignment_status": "matched",
                "similarity": 0.88,
                "filler_candidates": [{"token": "那个", "offset": 0}],
            },
            {
                "segment_id": "seg_0002",
                "start": 4.0,
                "end": 8.5,
                "asr_text": "读错了重来",
                "alignment_status": "low_similarity",
                "similarity": 0.35,
                "filler_candidates": [],
            },
        ],
        "policy": {"never_auto_delete_below_confidence": 0.75, "require_user_for_uncertain": True},
        "expected": {"seg_0001": "uncertain", "seg_0002": "uncertain"},
    },
]


def _evaluate(decision: dict[str, Any], expected: dict[str, str]) -> dict[str, Any]:
    """对比期望 action 与模型输出。"""
    actual: dict[str, str] = {}
    for d in decision.get("decisions", []):
        actual[d["segment_id"]] = d.get("action", "unknown")

    matches = sum(1 for sid, exp in expected.items() if actual.get(sid) == exp)
    total = len(expected)
    return {
        "expected": expected,
        "actual": actual,
        "match_count": matches,
        "total": total,
        "match_rate": round(matches / total, 2) if total else 0.0,
    }


def _write_report(run_dir: Path, report: dict[str, Any]) -> Path:
    run_dir.mkdir(parents=True, exist_ok=True)
    out = run_dir / "report.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return out


def run_samples(
    *,
    use_pipeline: bool = False,
    project_id: str = "book_001",
    chapter_id: str = "chapter_001",
) -> dict[str, Any]:
    """执行真实 API 样本生成。"""
    config = LlmApiConfig.from_env()
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = ROOT / "reports" / "real_api_runs" / ts

    report: dict[str, Any] = {
        "round": "autonomous_real_api",
        "timestamp_utc": ts,
        "model": config.model,
        "base_url": config.base_url,
        "api_key_configured": config.is_configured,
        "samples": [],
        "pipeline": None,
        "errors": [],
        "api_calls": 0,
        "quality_summary": {},
    }

    if not config.is_configured:
        report["errors"].append(
            "HARD_BLOCK: 未检测到 LLM_API_KEY / OPENAI_API_KEY（.env 或环境变量）"
        )
        report["quality_summary"] = {"status": "blocked", "reason": "missing_api_key"}
        _write_report(run_dir, report)
        return report

    try:
        adapter = OpenAiCompatibleAdapter(config)
    except RuntimeError as exc:
        report["errors"].append(str(exc))
        report["quality_summary"] = {"status": "blocked", "reason": "adapter_init_failed"}
        _write_report(run_dir, report)
        return report

    for sample in SAMPLE_PAYLOADS:
        payload = {
            "chapter_id": sample["chapter_id"],
            "segments": sample["segments"],
            "policy": sample["policy"],
        }
        entry: dict[str, Any] = {
            "name": sample["name"],
            "chapter_id": sample["chapter_id"],
            "input_segment_count": len(sample["segments"]),
            "status": "pending",
        }
        try:
            decision = adapter.decide(payload)
            report["api_calls"] += 1
            eval_result = _evaluate(decision, sample["expected"])
            entry["status"] = "ok"
            entry["evaluation"] = eval_result
            entry["decisions_summary"] = {
                d["segment_id"]: {"action": d["action"], "confidence": d["confidence"]}
                for d in decision.get("decisions", [])
            }
            out_path = run_dir / f"{sample['name']}_decision.json"
            out_path.write_text(
                json.dumps(decision, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            entry["output_path"] = str(out_path.relative_to(ROOT))
        except Exception as exc:  # noqa: BLE001
            entry["status"] = "error"
            entry["error"] = str(exc)
            entry["traceback"] = traceback.format_exc()
            report["errors"].append(f"{sample['name']}: {exc}")
        report["samples"].append(entry)

    if use_pipeline:
        try:
            service = LlmCutService(root=ROOT)
            pipeline_result = service.run_llm_cut(project_id, chapter_id, adapter=adapter)
            report["api_calls"] += 1
            report["pipeline"] = {
                "status": "ok",
                "project_id": project_id,
                "chapter_id": chapter_id,
                "engine": pipeline_result.get("llm_engine"),
                "decision_count": len(pipeline_result.get("decisions", [])),
                "output_path": pipeline_result.get("_output_path"),
            }
        except Exception as exc:  # noqa: BLE001
            report["pipeline"] = {"status": "error", "error": str(exc)}
            report["errors"].append(f"pipeline: {exc}")

    ok_samples = [s for s in report["samples"] if s.get("status") == "ok"]
    if ok_samples:
        avg_rate = sum(s["evaluation"]["match_rate"] for s in ok_samples) / len(ok_samples)
        report["quality_summary"] = {
            "status": "completed" if not report["errors"] else "partial",
            "samples_ok": len(ok_samples),
            "samples_total": len(SAMPLE_PAYLOADS),
            "avg_expected_action_match_rate": round(avg_rate, 2),
        }
    else:
        report["quality_summary"] = {
            "status": "failed",
            "samples_ok": 0,
            "samples_total": len(SAMPLE_PAYLOADS),
        }

    report["run_dir"] = str(run_dir.relative_to(ROOT))
    _write_report(run_dir, report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="真实 LLM API 验证")
    parser.add_argument(
        "--pipeline",
        action="store_true",
        help="额外对 book_001/chapter_001 跑完整 LlmCutService",
    )
    parser.add_argument("--project-id", default="book_001")
    parser.add_argument("--chapter-id", default="chapter_001")
    args = parser.parse_args()

    report = run_samples(
        use_pipeline=args.pipeline,
        project_id=args.project_id,
        chapter_id=args.chapter_id,
    )

    print(json.dumps(report, ensure_ascii=False, indent=2))

    if report["errors"] and report["api_calls"] == 0:
        return 2
    if report["errors"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
