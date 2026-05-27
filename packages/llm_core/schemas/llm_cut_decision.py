# -*- coding: utf-8 -*-
"""llm_cut_decision.json schema 定义。"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any

VALID_ACTIONS = frozenset({"keep", "delete", "uncertain"})
VALID_REASON_TYPES = frozenset({
    "matches_source",
    "restart_phrase",
    "off_script",
    "filler",
    "misread",
    "ambiguous_filler",
    "low_confidence",
})

AUTO_DELETE_MIN_CONFIDENCE = 0.75


@dataclass
class SuggestedCut:
    """建议切点（基于 segment 时间戳 ± padding）。"""

    start: float
    end: float
    pre_padding: float = 0.08
    post_padding: float = 0.12

    def validate(self) -> list[str]:
        """校验切点。"""
        if self.end <= self.start:
            return ["suggested_cut: end 必须大于 start"]
        return []


@dataclass
class LlmDecision:
    """单 segment 机切决策。"""

    segment_id: str
    action: str
    reason_type: str
    reason: str
    suggested_cut: SuggestedCut | None
    confidence: float

    def validate(self) -> list[str]:
        """校验决策项。"""
        errors: list[str] = []
        if self.action not in VALID_ACTIONS:
            errors.append(f"{self.segment_id}: 非法 action {self.action}")
        if self.reason_type not in VALID_REASON_TYPES:
            errors.append(f"{self.segment_id}: 非法 reason_type {self.reason_type}")
        if not 0.0 <= self.confidence <= 1.0:
            errors.append(f"{self.segment_id}: confidence 必须在 0~1")
        # 低置信度不得单独 delete
        if self.action == "delete" and self.confidence < AUTO_DELETE_MIN_CONFIDENCE:
            errors.append(
                f"{self.segment_id}: confidence < {AUTO_DELETE_MIN_CONFIDENCE} 不得 delete"
            )
        if self.suggested_cut:
            errors.extend(self.suggested_cut.validate())
        return errors


@dataclass
class LlmCutDecision:
    """章节 LLM 机切建议集合。"""

    chapter_id: str
    llm_engine: str
    decisions: list[LlmDecision] = field(default_factory=list)
    created_at: str = ""

    def __post_init__(self) -> None:
        if not self.created_at:
            self.created_at = datetime.now().replace(microsecond=0).isoformat()

    def validate(self) -> list[str]:
        """校验完整决策。"""
        errors: list[str] = []
        if not self.chapter_id.strip():
            errors.append("chapter_id 不能为空")
        if not self.decisions:
            errors.append("decisions 不能为空")
        for d in self.decisions:
            errors.extend(d.validate())
        return errors

    def to_dict(self) -> dict[str, Any]:
        """转为 JSON 可序列化字典。"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LlmCutDecision:
        """从字典反序列化。"""
        decisions: list[LlmDecision] = []
        for raw in data.get("decisions", []):
            sc = raw.get("suggested_cut")
            suggested = SuggestedCut(**sc) if sc else None
            decisions.append(
                LlmDecision(
                    segment_id=raw["segment_id"],
                    action=raw["action"],
                    reason_type=raw["reason_type"],
                    reason=raw["reason"],
                    suggested_cut=suggested,
                    confidence=float(raw["confidence"]),
                )
            )
        return cls(
            chapter_id=data["chapter_id"],
            llm_engine=data.get("llm_engine", "mock"),
            decisions=decisions,
            created_at=data.get("created_at", ""),
        )
