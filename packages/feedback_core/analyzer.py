# -*- coding: utf-8 -*-
"""反馈分析 — 比较 model 与 user 决策，生成 lesson。"""

from __future__ import annotations

from datetime import datetime
from typing import Any


def analyze_feedback(
    chapter_id: str,
    llm_decision: dict[str, Any],
    user_review: dict[str, Any],
) -> dict[str, Any]:
    """比较 LLM 建议与用户最终决策，输出 feedback_record。"""
    llm_map = {d["segment_id"]: d for d in llm_decision.get("decisions", [])}
    user_map = {d["segment_id"]: d for d in user_review.get("decisions", [])}

    items: list[dict[str, Any]] = []
    stats = {
        "total_segments": 0,
        "agreement_count": 0,
        "disagreement_count": 0,
        "false_delete_risk": 0,
        "user_override_to_keep": 0,
        "user_override_to_delete": 0,
        "uncertain_resolved": 0,
    }

    all_seg_ids = set(llm_map.keys()) | set(user_map.keys())
    for seg_id in sorted(all_seg_ids):
        model = llm_map.get(seg_id, {})
        user = user_map.get(seg_id, {})
        model_action = model.get("action", "unknown")
        user_action = user.get("user_action", "unknown")

        stats["total_segments"] += 1
        agreed = model_action == user_action
        if agreed:
            stats["agreement_count"] += 1
        else:
            stats["disagreement_count"] += 1

        lesson = ""
        if model_action == "delete" and user_action == "keep":
            stats["false_delete_risk"] += 1
            stats["user_override_to_keep"] += 1
            lesson = "模型建议删除但用户保留 — 可能误删正文，降低 delete 置信度阈值"
        elif model_action == "keep" and user_action == "delete":
            stats["user_override_to_delete"] += 1
            lesson = "模型建议保留但用户删除 — 补充 off_script/restart 规则"
        elif model_action == "uncertain":
            stats["uncertain_resolved"] += 1
            lesson = f"uncertain 已人工决策为 {user_action}"

        items.append(
            {
                "segment_id": seg_id,
                "model_action": model_action,
                "user_action": user_action,
                "agreed": agreed,
                "model_confidence": model.get("confidence"),
                "lesson": lesson or ("一致，无需调整" if agreed else "需复盘"),
            }
        )

    return {
        "chapter_id": chapter_id,
        "feedback_session_id": user_review.get("review_session_id", ""),
        "items": items,
        "stats": stats,
        "summary": _build_summary(stats),
        "created_at": datetime.now().replace(microsecond=0).isoformat(),
    }


def _build_summary(stats: dict[str, int]) -> str:
    """生成中文摘要。"""
    total = stats.get("total_segments", 0)
    agree = stats.get("agreement_count", 0)
    false_del = stats.get("false_delete_risk", 0)
    rate = (agree / total * 100) if total else 0
    return (
        f"共 {total} 段，一致率 {rate:.1f}%，"
        f"误删风险 {false_del} 次，"
        f"用户改 keep {stats.get('user_override_to_keep', 0)} 次"
    )
