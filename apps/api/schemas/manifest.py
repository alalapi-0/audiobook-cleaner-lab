# -*- coding: utf-8 -*-
"""Manifest JSON schema 定义 — 对齐 docs/DATA_MODEL.md。"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ChapterStatus(str, Enum):
    """章节处理状态枚举。"""

    PENDING = "pending"
    IMPORTED = "imported"
    ASR_DONE = "asr_done"
    ALIGNED = "aligned"
    REVIEWED = "reviewed"
    EXPORTED = "exported"


@dataclass
class ChapterSummary:
    """project_manifest 中的章节摘要。"""

    chapter_id: str
    title: str
    status: str
    order: int

    def validate(self) -> list[str]:
        """校验字段合法性，返回错误列表。"""
        errors: list[str] = []
        if not self.chapter_id.strip():
            errors.append("chapter_id 不能为空")
        if not self.title.strip():
            errors.append("title 不能为空")
        valid_status = {s.value for s in ChapterStatus}
        if self.status not in valid_status:
            errors.append(f"status 必须是 {sorted(valid_status)} 之一")
        if self.order < 1:
            errors.append("order 必须 >= 1")
        return errors


@dataclass
class ProjectDefaults:
    """项目默认 Adapter 与导出配置。"""

    asr_engine: str = "mock"
    llm_engine: str = "mock"
    export_format: str = "mp3"


@dataclass
class ProjectManifest:
    """书籍级项目元数据。"""

    project_id: str
    book_title: str
    language: str
    created_at: str
    updated_at: str
    chapters: list[ChapterSummary] = field(default_factory=list)
    defaults: ProjectDefaults = field(default_factory=ProjectDefaults)

    def validate(self) -> list[str]:
        """校验 manifest 字段。"""
        errors: list[str] = []
        if not self.project_id.strip():
            errors.append("project_id 不能为空")
        if not self.book_title.strip():
            errors.append("book_title 不能为空")
        if not self.language.strip():
            errors.append("language 不能为空")
        chapter_ids = [c.chapter_id for c in self.chapters]
        if len(chapter_ids) != len(set(chapter_ids)):
            errors.append("chapters 中存在重复 chapter_id")
        for ch in self.chapters:
            errors.extend(ch.validate())
        return errors

    def to_dict(self) -> dict[str, Any]:
        """转为可 JSON 序列化的字典。"""
        data = asdict(self)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProjectManifest:
        """从字典反序列化。"""
        defaults_raw = data.get("defaults") or {}
        defaults = ProjectDefaults(**defaults_raw)
        chapters = [ChapterSummary(**c) for c in data.get("chapters", [])]
        return cls(
            project_id=data["project_id"],
            book_title=data["book_title"],
            language=data["language"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            chapters=chapters,
            defaults=defaults,
        )


@dataclass
class ChapterArtifacts:
    """章节流水线产物路径。"""

    transcript: str
    normalized_source: str
    normalized_asr: str
    alignment: str
    llm_decision: str
    cut_plan: str
    user_review: str
    export: str

    @classmethod
    def default_paths(cls, project_id: str, chapter_id: str) -> ChapterArtifacts:
        """按 DATA_MODEL 约定生成默认产物路径。"""
        return cls(
            transcript=f"data/transcripts/{project_id}/{chapter_id}.json",
            normalized_source=f"data/normalized/{project_id}/{chapter_id}_source.json",
            normalized_asr=f"data/normalized/{project_id}/{chapter_id}_asr.json",
            alignment=f"data/alignments/{project_id}/{chapter_id}.json",
            llm_decision=f"data/cut_plans/{project_id}/{chapter_id}_llm.json",
            cut_plan=f"data/cut_plans/{project_id}/{chapter_id}.json",
            user_review=f"data/reviews/{project_id}/{chapter_id}.json",
            export=f"data/exports/{project_id}/{chapter_id}_clean.mp3",
        )


@dataclass
class ChapterManifest:
    """章节级素材路径与处理状态。"""

    chapter_id: str
    project_id: str
    title: str
    source_audio: str
    source_text: str
    status: str
    artifacts: ChapterArtifacts
    created_at: str

    def validate(self) -> list[str]:
        """校验章节 manifest 字段。"""
        errors: list[str] = []
        if not self.chapter_id.strip():
            errors.append("chapter_id 不能为空")
        if not self.project_id.strip():
            errors.append("project_id 不能为空")
        if not self.title.strip():
            errors.append("title 不能为空")
        valid_status = {s.value for s in ChapterStatus}
        if self.status not in valid_status:
            errors.append(f"status 必须是 {sorted(valid_status)} 之一")
        for path_field in ("source_audio", "source_text"):
            if not getattr(self, path_field).strip():
                errors.append(f"{path_field} 不能为空")
        return errors

    def to_dict(self) -> dict[str, Any]:
        """转为可 JSON 序列化的字典。"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ChapterManifest:
        """从字典反序列化。"""
        artifacts = ChapterArtifacts(**data["artifacts"])
        return cls(
            chapter_id=data["chapter_id"],
            project_id=data["project_id"],
            title=data["title"],
            source_audio=data["source_audio"],
            source_text=data["source_text"],
            status=data["status"],
            artifacts=artifacts,
            created_at=data["created_at"],
        )


def iso_now() -> str:
    """返回 ISO 格式当前时间字符串。"""
    return datetime.now().replace(microsecond=0).isoformat()
