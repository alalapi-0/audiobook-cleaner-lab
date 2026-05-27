# -*- coding: utf-8 -*-
"""音频导出流水线服务。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apps.api.schemas.manifest import ChapterStatus, iso_now
from apps.api.services.manifest_service import ManifestService
from packages.audio_core.ffmpeg_exporter import FfmpegExporter

ROOT = Path(__file__).resolve().parents[2]


class ExportService:
    """章节 FFmpeg 导出服务。"""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or ROOT
        self.manifest_service = ManifestService(root=self.root)
        self.exporter = FfmpegExporter()

    def _resolve_path(self, rel_path: str) -> Path:
        path = Path(rel_path)
        return path if path.is_absolute() else self.root / path

    def export_chapter(
        self,
        project_id: str,
        chapter_id: str,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        """根据 cut_plan 导出干净音频。"""
        chapter = self.manifest_service.load_chapter(project_id, chapter_id)
        cut_plan_path = self._resolve_path(chapter.artifacts.cut_plan)
        if not cut_plan_path.is_file():
            raise FileNotFoundError(f"cut_plan 不存在: {chapter.artifacts.cut_plan}")

        cut_plan = json.loads(cut_plan_path.read_text(encoding="utf-8"))
        result = self.exporter.export(cut_plan, self.root, dry_run=dry_run)

        report_rel = f"data/logs/{project_id}/{chapter_id}_export_report.json"
        report_path = self._resolve_path(report_rel)
        self.exporter.write_export_report(result, chapter_id, report_path)

        if result.success and not dry_run:
            chapter.status = ChapterStatus.EXPORTED.value
            chapter_path = self.manifest_service.chapter_manifest_path(
                project_id, chapter_id
            )
            chapter_path.write_text(
                json.dumps(chapter.to_dict(), ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            project = self.manifest_service.load_project(project_id)
            for ch in project.chapters:
                if ch.chapter_id == chapter_id:
                    ch.status = ChapterStatus.EXPORTED.value
            project.updated_at = iso_now()
            project_path = self.manifest_service.project_manifest_path(project_id)
            project_path.write_text(
                json.dumps(project.to_dict(), ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

        report = result.to_report(chapter_id)
        report["export_report_path"] = report_rel
        return report
