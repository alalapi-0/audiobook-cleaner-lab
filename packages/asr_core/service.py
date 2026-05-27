# -*- coding: utf-8 -*-
"""ASR 流水线服务 — 运行 Adapter 并更新 chapter manifest。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apps.api.schemas.manifest import ChapterStatus
from apps.api.services.manifest_service import ManifestService
from packages.asr_core.base import AsrAdapter

ROOT = Path(__file__).resolve().parents[2]


class AsrService:
    """章节 ASR 转写服务。"""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or ROOT
        self.manifest_service = ManifestService(root=self.root)

    def _resolve_path(self, rel_path: str) -> Path:
        path = Path(rel_path)
        return path if path.is_absolute() else self.root / path

    def _write_transcript(self, rel_path: str, data: dict[str, Any]) -> Path:
        """写入 transcript.json。"""
        out_path = self._resolve_path(rel_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return out_path

    def _update_chapter_status(self, project_id: str, chapter_id: str) -> None:
        """将章节与项目 manifest 状态更新为 asr_done。"""
        chapter = self.manifest_service.load_chapter(project_id, chapter_id)
        chapter.status = ChapterStatus.ASR_DONE.value
        chapter_path = self.manifest_service.chapter_manifest_path(project_id, chapter_id)
        chapter_path.write_text(
            json.dumps(chapter.to_dict(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        project = self.manifest_service.load_project(project_id)
        for ch in project.chapters:
            if ch.chapter_id == chapter_id:
                ch.status = ChapterStatus.ASR_DONE.value
        from apps.api.schemas.manifest import iso_now

        project.updated_at = iso_now()
        project_path = self.manifest_service.project_manifest_path(project_id)
        project_path.write_text(
            json.dumps(project.to_dict(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def run_asr(
        self,
        project_id: str,
        chapter_id: str,
        adapter: AsrAdapter,
    ) -> dict[str, Any]:
        """对指定章节运行 ASR Adapter。"""
        chapter = self.manifest_service.load_chapter(project_id, chapter_id)
        audio_path = self._resolve_path(chapter.source_audio)
        if not audio_path.is_file():
            raise FileNotFoundError(f"音频文件不存在: {chapter.source_audio}")

        transcript = adapter.transcribe(
            audio_path=str(audio_path),
            chapter_id=chapter_id,
            project_id=project_id,
        )
        out_path = self._write_transcript(chapter.artifacts.transcript, transcript)
        self._update_chapter_status(project_id, chapter_id)
        transcript["_output_path"] = str(out_path.relative_to(self.root))
        return transcript
