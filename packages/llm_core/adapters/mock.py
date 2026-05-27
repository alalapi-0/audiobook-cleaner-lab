# -*- coding: utf-8 -*-
"""Mock LLM Adapter — 基于 alignment status 规则输出机切建议，不调用真实 API。"""

from __future__ import annotations

from typing import Any

from packages.llm_core.base import LlmAdapter
from packages.llm_core.schemas.llm_cut_decision import (
    AUTO_DELETE_MIN_CONFIDENCE,
    LlmCutDecision,
    LlmDecision,
    SuggestedCut,
)

# alignment status → 决策规则映射
_STATUS_RULES: dict[str, tuple[str, str, str, float]] = {
    # (action, reason_type, reason, confidence)
    "matched": ("keep", "matches_source", "与原文一致，保留", 0.96),
    "extra_candidate": ("delete", "restart_phrase", "该片段是重读前的废弃内容，不属于原文", 0.87),
    "repeated": ("delete", "misread", "重复读段，保留最后一次匹配，前序建议删除", 0.85),
    "low_similarity": ("uncertain", "low_confidence", "相似度过低，需人工试听确认", 0.45),
    "uncertain": ("uncertain", "ambiguous_filler", "对齐不确定，需人工确认", 0.52),
    "missing": ("keep", "matches_source", "原文有但 ASR 无对应，不删音频", 0.90),
}


class MockLlmAdapter(LlmAdapter):
    """规则驱动的 mock LLM，严格遵循 LLM_CUT_DECISION_PROTOCOL 安全规则。"""

    @property
    def engine_name(self) -> str:
        return "mock"

    def _build_decision(
        self,
        segment_id: str,
        alignment_status: str,
        start: float,
        end: float,
        filler_candidates: list[dict],
    ) -> LlmDecision:
        """根据 alignment status 构建单条决策。"""
        action, reason_type, reason, confidence = _STATUS_RULES.get(
            alignment_status,
            ("uncertain", "low_confidence", "未知状态，需人工确认", 0.40),
        )

        # filler 候选：若已是 matched 但有 filler，降为 uncertain
        if filler_candidates and alignment_status == "matched":
            action = "uncertain"
            reason_type = "ambiguous_filler"
            reason = "「语气词」可能是 filler 也可能是正文，需人工试听"
            confidence = 0.55

        # 安全规则：低置信度不得 delete
        if action == "delete" and confidence < AUTO_DELETE_MIN_CONFIDENCE:
            action = "uncertain"
            reason_type = "low_confidence"
            reason = f"置信度 {confidence} 低于阈值，不得自动删除"
            confidence = min(confidence, 0.60)

        suggested = None
        if action in ("delete", "uncertain") and end > start:
            suggested = SuggestedCut(start=start, end=end)

        return LlmDecision(
            segment_id=segment_id,
            action=action,
            reason_type=reason_type,
            reason=reason,
            suggested_cut=suggested,
            confidence=confidence,
        )

    def decide(self, payload: dict[str, Any]) -> dict[str, Any]:
        """基于 payload 中的 segments 列表输出 llm_cut_decision。"""
        chapter_id = payload["chapter_id"]
        segments = payload.get("segments", [])

        decisions: list[LlmDecision] = []
        for seg in segments:
            seg_id = seg["segment_id"]
            status = seg.get("alignment_status", "uncertain")
            start = float(seg.get("start", 0.0))
            end = float(seg.get("end", 0.0))
            fillers = seg.get("filler_candidates", [])

            decisions.append(
                self._build_decision(seg_id, status, start, end, fillers)
            )

        result = LlmCutDecision(
            chapter_id=chapter_id,
            llm_engine=self.engine_name,
            decisions=decisions,
        )
        errors = result.validate()
        if errors:
            raise ValueError(f"mock llm_cut_decision 校验失败: {'; '.join(errors)}")
        return result.to_dict()
