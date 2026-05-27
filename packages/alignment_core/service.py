# -*- coding: utf-8 -*-
"""对齐流水线服务。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apps.api.schemas.manifest import ChapterStatus, iso_now
from apps.api.services.manifest_service import ManifestService
from packages.alignment_core.aligner import BaselineAligner

ROOT = Path(__file__).resolve().parents[2]


class AlignmentService:
    """章节对齐服务。"""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or ROOT
        self.manifest_service = ManifestService(root=self.root)
        self.aligner = BaselineAligner()

    def _resolve_path(self, rel_path: str) -> Path:
        path = Path(rel_path)
        return path if path.is_absolute() else self.root / path

    def _write_json(self, rel_path: str, data: dict[str, Any]) -> Path:
        out = self._resolve_path(rel_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return out

    def _update_status(self, project_id: str, chapter_id: str) -> None:
        """更新章节与项目 manifest 状态为 aligned。"""
        chapter = self.manifest_service.load_chapter(project_id, chapter_id)
        chapter.status = ChapterStatus.ALIGNED.value
        chapter_path = self.manifest_service.chapter_manifest_path(project_id, chapter_id)
        chapter_path.write_text(
            json.dumps(chapter.to_dict(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        project = self.manifest_service.load_project(project_id)
        for ch in project.chapters:
            if ch.chapter_id == chapter_id:
                ch.status = ChapterStatus.ALIGNED.value
        project.updated_at = iso_now()
        project_path = self.manifest_service.project_manifest_path(project_id)
        project_path.write_text(
            json.dumps(project.to_dict(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def align_chapter(self, project_id: str, chapter_id: str) -> dict[str, Any]:
        """对指定章节执行对齐。"""
        chapter = self.manifest_service.load_chapter(project_id, chapter_id)

        source_path = self._resolve_path(chapter.artifacts.normalized_source)
        asr_path = self._resolve_path(chapter.artifacts.normalized_asr)
        if not source_path.is_file():
            raise FileNotFoundError(f"normalized source 不存在: {source_path}")
        if not asr_path.is_file():
            raise FileNotFoundError(f"normalized asr 不存在: {asr_path}")

        source_data = json.loads(source_path.read_text(encoding="utf-8"))
        asr_data = json.loads(asr_path.read_text(encoding="utf-8"))

        alignment = self.aligner.align(
            chapter_id=chapter_id,
            source_text=source_data["normalized_text"],
            asr_segments=asr_data["segments"],
        )
        out_path = self._write_json(chapter.artifacts.alignment, alignment.to_dict())
        self._update_status(project_id, chapter_id)

        result = alignment.to_dict()
        result["_output_path"] = str(out_path.relative_to(self.root))
        return result
