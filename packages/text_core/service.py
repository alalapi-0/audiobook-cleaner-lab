# -*- coding: utf-8 -*-
"""文本清洗流水线服务。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apps.api.services.manifest_service import ManifestService
from packages.text_core.config import NormalizationConfig
from packages.text_core.normalizers import normalize_asr_segments, normalize_source_text

ROOT = Path(__file__).resolve().parents[2]


class TextNormalizationService:
    """章节文本规范化服务。"""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or ROOT
        self.manifest_service = ManifestService(root=self.root)
        self.config = NormalizationConfig.default()

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

    def normalize_chapter(self, project_id: str, chapter_id: str) -> dict[str, Any]:
        """对指定章节执行原文与 ASR 文本清洗。"""
        chapter = self.manifest_service.load_chapter(project_id, chapter_id)

        # 原文清洗
        source_path = self._resolve_path(chapter.source_text)
        if not source_path.is_file():
            raise FileNotFoundError(f"原文不存在: {chapter.source_text}")
        raw_text = source_path.read_text(encoding="utf-8")
        normalized_source = normalize_source_text(
            raw_text,
            chapter_id=chapter_id,
            source_path=chapter.source_text,
            config=self.config,
        )
        source_out = self._write_json(
            chapter.artifacts.normalized_source,
            normalized_source,
        )

        # ASR 清洗
        transcript_path = self._resolve_path(chapter.artifacts.transcript)
        if not transcript_path.is_file():
            raise FileNotFoundError(
                f"transcript 不存在，请先运行 ASR: {chapter.artifacts.transcript}"
            )
        transcript = json.loads(transcript_path.read_text(encoding="utf-8"))
        normalized_asr = normalize_asr_segments(transcript, config=self.config)
        asr_out = self._write_json(chapter.artifacts.normalized_asr, normalized_asr)

        return {
            "normalized_source": str(source_out.relative_to(self.root)),
            "normalized_asr": str(asr_out.relative_to(self.root)),
        }
