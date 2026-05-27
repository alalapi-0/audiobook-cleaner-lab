# -*- coding: utf-8 -*-
"""反馈闭环服务。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apps.api.services.manifest_service import ManifestService
from packages.feedback_core.analyzer import analyze_feedback

ROOT = Path(__file__).resolve().parents[2]


class FeedbackService:
    """反馈记录与汇总服务。"""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or ROOT
        self.manifest_service = ManifestService(root=self.root)

    def _resolve_path(self, rel_path: str) -> Path:
        path = Path(rel_path)
        return path if path.is_absolute() else self.root / path

    def generate_feedback(self, project_id: str, chapter_id: str) -> dict[str, Any]:
        """生成章节 feedback_record。"""
        chapter = self.manifest_service.load_chapter(project_id, chapter_id)

        llm_path = self._resolve_path(chapter.artifacts.llm_decision)
        review_path = self._resolve_path(chapter.artifacts.user_review)
        if not llm_path.is_file():
            raise FileNotFoundError(f"llm_decision 不存在: {llm_path}")
        if not review_path.is_file():
            raise FileNotFoundError(f"user_review 不存在: {review_path}")

        llm = json.loads(llm_path.read_text(encoding="utf-8"))
        review = json.loads(review_path.read_text(encoding="utf-8"))
        record = analyze_feedback(chapter_id, llm, review)

        out_rel = f"data/logs/{project_id}/{chapter_id}_feedback.json"
        out_path = self._resolve_path(out_rel)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            json.dumps(record, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        record["_output_path"] = out_rel
        return record
