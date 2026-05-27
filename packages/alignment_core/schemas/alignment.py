# -*- coding: utf-8 -*-
"""alignment.json schema 定义。"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any

VALID_STATUSES = frozenset({
    "matched",
    "extra_candidate",
    "missing",
    "repeated",
    "uncertain",
    "low_similarity",
})


@dataclass
class SourceRange:
    """原文 char 偏移范围。"""

    start_char: int
    end_char: int


@dataclass
class AlignmentItem:
    """单条对齐结果。"""

    alignment_id: str
    asr_segment_id: str | None
    source_range: SourceRange | None
    asr_text: str | None
    source_text: str | None
    similarity: float
    status: str

    def validate(self) -> list[str]:
        """校验对齐项。"""
        errors: list[str] = []
        if self.status not in VALID_STATUSES:
            errors.append(f"{self.alignment_id}: 非法 status {self.status}")
        if not 0.0 <= self.similarity <= 1.0:
            errors.append(f"{self.alignment_id}: similarity 必须在 0~1")
        return errors


@dataclass
class Alignment:
    """章节对齐结果。"""

    chapter_id: str
    alignment_engine: str
    items: list[AlignmentItem] = field(default_factory=list)
    created_at: str = ""

    def __post_init__(self) -> None:
        if not self.created_at:
            self.created_at = datetime.now().replace(microsecond=0).isoformat()

    def validate(self) -> list[str]:
        """校验 alignment 完整性。"""
        errors: list[str] = []
        if not self.chapter_id.strip():
            errors.append("chapter_id 不能为空")
        if not self.items:
            errors.append("items 不能为空")
        for item in self.items:
            errors.extend(item.validate())
        return errors

    def to_dict(self) -> dict[str, Any]:
        """转为 JSON 可序列化字典。"""
        data = asdict(self)
        # source_range None 保持 null
        for item in data["items"]:
            if item["source_range"] is None:
                continue
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Alignment:
        """从字典反序列化。"""
        items: list[AlignmentItem] = []
        for raw in data.get("items", []):
            sr = raw.get("source_range")
            source_range = SourceRange(**sr) if sr else None
            items.append(
                AlignmentItem(
                    alignment_id=raw["alignment_id"],
                    asr_segment_id=raw.get("asr_segment_id"),
                    source_range=source_range,
                    asr_text=raw.get("asr_text"),
                    source_text=raw.get("source_text"),
                    similarity=float(raw.get("similarity", 0.0)),
                    status=raw["status"],
                )
            )
        return cls(
            chapter_id=data["chapter_id"],
            alignment_engine=data.get("alignment_engine", "baseline_v1"),
            items=items,
            created_at=data.get("created_at", ""),
        )
