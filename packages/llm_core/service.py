# -*- coding: utf-8 -*-
"""LLM 机切流水线服务。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apps.api.services.manifest_service import ManifestService
from packages.llm_core.adapters.mock import MockLlmAdapter
from packages.llm_core.base import LlmAdapter

ROOT = Path(__file__).resolve().parents[2]


class LlmCutService:
    """章节 LLM 机切建议服务。"""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or ROOT
        self.manifest_service = ManifestService(root=self.root)

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

    def _build_payload(
        self,
        chapter_id: str,
        alignment: dict[str, Any],
        transcript: dict[str, Any],
        normalized_asr: dict[str, Any],
    ) -> dict[str, Any]:
        """组装 LLM 输入 payload。"""
        # segment_id → transcript segment
        ts_map = {s["segment_id"]: s for s in transcript.get("segments", [])}
        # segment_id → filler candidates
        filler_map = {
            s["segment_id"]: s.get("filler_candidates", [])
            for s in normalized_asr.get("segments", [])
        }

        segments: list[dict[str, Any]] = []
        for item in alignment.get("items", []):
            seg_id = item.get("asr_segment_id")
            if not seg_id:
                continue
            ts = ts_map.get(seg_id, {})
            segments.append(
                {
                    "segment_id": seg_id,
                    "start": ts.get("start", 0.0),
                    "end": ts.get("end", 0.0),
                    "asr_text": item.get("asr_text", ""),
                    "alignment_status": item.get("status", "uncertain"),
                    "similarity": item.get("similarity", 0.0),
                    "filler_candidates": filler_map.get(seg_id, []),
                }
            )

        return {
            "chapter_id": chapter_id,
            "segments": segments,
            "policy": {
                "never_auto_delete_below_confidence": 0.75,
                "require_user_for_uncertain": True,
            },
        }

    def run_llm_cut(
        self,
        project_id: str,
        chapter_id: str,
        adapter: LlmAdapter | None = None,
    ) -> dict[str, Any]:
        """对指定章节运行 LLM 机切建议。"""
        chapter = self.manifest_service.load_chapter(project_id, chapter_id)

        alignment_path = self._resolve_path(chapter.artifacts.alignment)
        transcript_path = self._resolve_path(chapter.artifacts.transcript)
        asr_path = self._resolve_path(chapter.artifacts.normalized_asr)

        for p, label in [
            (alignment_path, "alignment"),
            (transcript_path, "transcript"),
            (asr_path, "normalized_asr"),
        ]:
            if not p.is_file():
                raise FileNotFoundError(f"{label} 不存在: {p}")

        alignment = json.loads(alignment_path.read_text(encoding="utf-8"))
        transcript = json.loads(transcript_path.read_text(encoding="utf-8"))
        normalized_asr = json.loads(asr_path.read_text(encoding="utf-8"))

        payload = self._build_payload(chapter_id, alignment, transcript, normalized_asr)
        llm = adapter or MockLlmAdapter()
        decision = llm.decide(payload)

        out_path = self._write_json(chapter.artifacts.llm_decision, decision)
        decision["_output_path"] = str(out_path.relative_to(self.root))
        return decision
