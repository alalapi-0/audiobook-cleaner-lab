# -*- coding: utf-8 -*-
"""Review 数据组装与 user_review / cut_plan 保存服务。"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from apps.api.services.manifest_service import ManifestService

ROOT = Path(__file__).resolve().parents[3]


class ReviewService:
    """人工 Review 服务。"""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or ROOT
        self.manifest_service = ManifestService(root=self.root)

    def _resolve_path(self, rel_path: str) -> Path:
        path = Path(rel_path)
        return path if path.is_absolute() else self.root / path

    def _read_json(self, path: Path) -> dict[str, Any]:
        if not path.is_file():
            raise FileNotFoundError(f"文件不存在: {path}")
        return json.loads(path.read_text(encoding="utf-8"))

    def _write_json(self, rel_path: str, data: dict[str, Any]) -> Path:
        out = self._resolve_path(rel_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return out

    def get_review_data(self, project_id: str, chapter_id: str) -> dict[str, Any]:
        """组装 Review 页面所需全部 JSON 数据。"""
        chapter = self.manifest_service.load_chapter(project_id, chapter_id)
        artifacts = chapter.artifacts

        def load_artifact(rel: str, label: str) -> dict[str, Any]:
            path = self._resolve_path(rel)
            if not path.is_file():
                raise FileNotFoundError(f"{label} 不存在，请先完成前置流水线: {rel}")
            return self._read_json(path)

        normalized_source = load_artifact(artifacts.normalized_source, "normalized_source")
        normalized_asr = load_artifact(artifacts.normalized_asr, "normalized_asr")
        transcript = load_artifact(artifacts.transcript, "transcript")
        alignment = load_artifact(artifacts.alignment, "alignment")
        llm_decision = load_artifact(artifacts.llm_decision, "llm_decision")

        # 合并 segment 视图
        ts_map = {s["segment_id"]: s for s in transcript.get("segments", [])}
        align_map = {
            item["asr_segment_id"]: item
            for item in alignment.get("items", [])
            if item.get("asr_segment_id")
        }
        decision_map = {d["segment_id"]: d for d in llm_decision.get("decisions", [])}
        asr_map = {s["segment_id"]: s for s in normalized_asr.get("segments", [])}

        segments: list[dict[str, Any]] = []
        for seg_id, ts in ts_map.items():
            align = align_map.get(seg_id, {})
            decision = decision_map.get(seg_id, {})
            asr_norm = asr_map.get(seg_id, {})
            segments.append(
                {
                    "segment_id": seg_id,
                    "start": ts.get("start"),
                    "end": ts.get("end"),
                    "asr_text": ts.get("text"),
                    "normalized_text": asr_norm.get("normalized_text"),
                    "alignment_status": align.get("status"),
                    "similarity": align.get("similarity"),
                    "source_text": align.get("source_text"),
                    "model_action": decision.get("action"),
                    "model_reason": decision.get("reason"),
                    "model_confidence": decision.get("confidence"),
                    "suggested_cut": decision.get("suggested_cut"),
                    "filler_candidates": asr_norm.get("filler_candidates", []),
                }
            )

        return {
            "project_id": project_id,
            "chapter_id": chapter_id,
            "title": chapter.title,
            "source_audio": chapter.source_audio,
            "normalized_source_text": normalized_source.get("normalized_text", ""),
            "segments": segments,
            "llm_engine": llm_decision.get("llm_engine"),
        }

    def save_review(
        self,
        project_id: str,
        chapter_id: str,
        user_decisions: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """保存 user_review.json 并生成 cut_plan.json。"""
        chapter = self.manifest_service.load_chapter(project_id, chapter_id)
        llm_path = self._resolve_path(chapter.artifacts.llm_decision)
        llm_decision = self._read_json(llm_path)
        llm_map = {d["segment_id"]: d for d in llm_decision.get("decisions", [])}

        now = datetime.now().replace(microsecond=0).isoformat()
        session_id = f"rev_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"

        review_decisions: list[dict[str, Any]] = []
        delete_ranges: list[dict[str, Any]] = []
        keep_ranges: list[dict[str, Any]] = []

        for ud in user_decisions:
            seg_id = ud["segment_id"]
            user_action = ud["user_action"]
            model = llm_map.get(seg_id, {})
            model_action = model.get("action", "uncertain")
            suggested = ud.get("user_adjusted_cut") or model.get("suggested_cut")

            review_decisions.append(
                {
                    "segment_id": seg_id,
                    "model_action": model_action,
                    "user_action": user_action,
                    "user_adjusted_cut": suggested,
                    "note": ud.get("note", ""),
                    "reviewed_at": now,
                }
            )

            if user_action == "delete" and suggested:
                delete_ranges.append(
                    {
                        "range_id": f"del_{len(delete_ranges) + 1:03d}",
                        "start": max(
                            0.0,
                            float(suggested["start"])
                            - float(suggested.get("pre_padding", 0.08)),
                        ),
                        "end": float(suggested["end"])
                        + float(suggested.get("post_padding", 0.12)),
                        "reason": model.get("reason_type", "user_confirmed"),
                        "source_segment_ids": [seg_id],
                        "confirmed_by_user": True,
                    }
                )
            elif user_action == "keep":
                # 从 transcript 获取时间戳
                transcript = self._read_json(
                    self._resolve_path(chapter.artifacts.transcript)
                )
                ts_map = {s["segment_id"]: s for s in transcript.get("segments", [])}
                ts = ts_map.get(seg_id, {})
                if ts:
                    keep_ranges.append(
                        {
                            "range_id": f"keep_{len(keep_ranges) + 1:03d}",
                            "start": ts.get("start", 0.0),
                            "end": ts.get("end", 0.0),
                            "source_segment_ids": [seg_id],
                        }
                    )

        user_review = {
            "chapter_id": chapter_id,
            "review_session_id": session_id,
            "decisions": review_decisions,
            "created_at": now,
        }
        self._write_json(chapter.artifacts.user_review, user_review)

        cut_plan = {
            "chapter_id": chapter_id,
            "source_audio": chapter.source_audio,
            "version": 1,
            "delete_ranges": delete_ranges,
            "keep_ranges": keep_ranges,
            "export": {
                "format": "mp3",
                "bitrate": "192k",
                "output_path": chapter.artifacts.export,
            },
            "updated_at": now,
        }
        self._write_json(chapter.artifacts.cut_plan, cut_plan)

        # 更新章节状态
        chapter.status = "reviewed"
        chapter_path = self.manifest_service.chapter_manifest_path(project_id, chapter_id)
        chapter_path.write_text(
            json.dumps(chapter.to_dict(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        return {
            "user_review_path": chapter.artifacts.user_review,
            "cut_plan_path": chapter.artifacts.cut_plan,
            "delete_count": len(delete_ranges),
            "keep_count": len(keep_ranges),
        }
