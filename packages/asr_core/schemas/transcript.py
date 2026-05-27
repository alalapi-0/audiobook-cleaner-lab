# -*- coding: utf-8 -*-
"""transcript.json schema 定义。"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class TranscriptSegment:
    """ASR segment 级时间戳。"""

    segment_id: str
    start: float
    end: float
    text: str
    confidence: float = 0.9

    def validate(self) -> list[str]:
        """校验 segment 字段。"""
        errors: list[str] = []
        if not self.segment_id.strip():
            errors.append("segment_id 不能为空")
        if self.end <= self.start:
            errors.append(f"{self.segment_id}: end 必须大于 start")
        if not self.text.strip():
            errors.append(f"{self.segment_id}: text 不能为空")
        if not 0.0 <= self.confidence <= 1.0:
            errors.append(f"{self.segment_id}: confidence 必须在 0~1")
        return errors


@dataclass
class Transcript:
    """ASR 转写结果。"""

    chapter_id: str
    project_id: str
    asr_engine: str
    duration_sec: float
    segments: list[TranscriptSegment] = field(default_factory=list)
    created_at: str = ""

    def __post_init__(self) -> None:
        if not self.created_at:
            self.created_at = datetime.now().replace(microsecond=0).isoformat()

    def validate(self) -> list[str]:
        """校验 transcript 完整性。"""
        errors: list[str] = []
        if not self.chapter_id.strip():
            errors.append("chapter_id 不能为空")
        if not self.project_id.strip():
            errors.append("project_id 不能为空")
        if self.duration_sec <= 0:
            errors.append("duration_sec 必须 > 0")
        if not self.segments:
            errors.append("segments 不能为空")
        seg_ids = [s.segment_id for s in self.segments]
        if len(seg_ids) != len(set(seg_ids)):
            errors.append("segments 中存在重复 segment_id")
        for seg in self.segments:
            errors.extend(seg.validate())
        return errors

    def to_dict(self) -> dict[str, Any]:
        """转为 JSON 可序列化字典。"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Transcript:
        """从字典反序列化。"""
        segments = [TranscriptSegment(**s) for s in data.get("segments", [])]
        return cls(
            chapter_id=data["chapter_id"],
            project_id=data["project_id"],
            asr_engine=data["asr_engine"],
            duration_sec=float(data["duration_sec"]),
            segments=segments,
            created_at=data.get("created_at", ""),
        )
