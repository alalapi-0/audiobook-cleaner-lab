#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Review 服务与 API 单元测试。"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.api.services.manifest_service import ManifestService  # noqa: E402
from apps.api.services.review_service import ReviewService  # noqa: E402
from packages.alignment_core.service import AlignmentService  # noqa: E402
from packages.asr_core.adapters import MockAsrAdapter  # noqa: E402
from packages.asr_core.service import AsrService  # noqa: E402
from packages.llm_core.service import LlmCutService  # noqa: E402
from packages.text_core.service import TextNormalizationService  # noqa: E402


def _make_wav(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(b"\x00\x00" * 16000)


def _run_full_pipeline(root: Path) -> None:
    """运行 Round 01–05 流水线。"""
    manifest = ManifestService(root=root)
    asr = AsrService(root=root)
    norm = TextNormalizationService(root=root)
    align = AlignmentService(root=root)
    llm = LlmCutService(root=root)

    audio = root / "data/raw_audio/book_001/chapter_001.wav"
    text = root / "data/source_text/book_001/chapter_001.txt"
    _make_wav(audio)
    text.parent.mkdir(parents=True, exist_ok=True)
    text.write_text("这是正确原文文本。后续段落内容。", encoding="utf-8")

    manifest.create_project("book_001", "测试书")
    manifest.add_chapter(
        project_id="book_001",
        chapter_id="chapter_001",
        title="第一章",
        source_audio="data/raw_audio/book_001/chapter_001.wav",
        source_text="data/source_text/book_001/chapter_001.txt",
    )
    asr.run_asr("book_001", "chapter_001", MockAsrAdapter())
    norm.normalize_chapter("book_001", "chapter_001")
    align.align_chapter("book_001", "chapter_001")
    llm.run_llm_cut("book_001", "chapter_001")


class TestReviewService(unittest.TestCase):
    """ReviewService 测试。"""

    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tmpdir.name)
        _run_full_pipeline(self.root)
        self.review = ReviewService(root=self.root)
        self.manifest = ManifestService(root=self.root)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_get_review_data(self) -> None:
        """获取 Review 数据含 segments。"""
        data = self.review.get_review_data("book_001", "chapter_001")
        self.assertEqual(data["chapter_id"], "chapter_001")
        self.assertGreater(len(data["segments"]), 0)
        self.assertIn("model_action", data["segments"][0])

    def test_save_review_cut_plan_confirmed(self) -> None:
        """保存 review 生成含 confirmed_by_user 的 cut_plan。"""
        data = self.review.get_review_data("book_001", "chapter_001")
        decisions = []
        for seg in data["segments"]:
            action = seg.get("model_action", "keep")
            if action not in ("keep", "delete", "uncertain"):
                action = "keep"
            decisions.append(
                {
                    "segment_id": seg["segment_id"],
                    "user_action": action,
                    "user_adjusted_cut": seg.get("suggested_cut"),
                }
            )

        result = self.review.save_review("book_001", "chapter_001", decisions)
        chapter = self.manifest.load_chapter("book_001", "chapter_001")
        cut_plan_path = self.root / chapter.artifacts.cut_plan
        self.assertTrue(cut_plan_path.is_file())

        cut_plan = json.loads(cut_plan_path.read_text(encoding="utf-8"))
        self.assertIn("delete_ranges", cut_plan)
        for dr in cut_plan["delete_ranges"]:
            self.assertTrue(dr.get("confirmed_by_user"))

        user_review_path = self.root / chapter.artifacts.user_review
        self.assertTrue(user_review_path.is_file())
        self.assertGreater(result["delete_count"] + result["keep_count"], 0)


class TestReviewApi(unittest.TestCase):
    """FastAPI Review 路由测试（需安装 fastapi）。"""

    def setUp(self) -> None:
        try:
            from fastapi.testclient import TestClient
            from apps.api.main import app
        except ImportError:
            self.skipTest("fastapi 未安装")
        if app is None:
            self.skipTest("FastAPI app 未初始化")
        self.client = TestClient(app)
        self._tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tmpdir.name)
        # 注意：ReviewService 使用全局 ROOT，API 测试仅测 health
        _run_full_pipeline(self.root)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_health(self) -> None:
        """健康检查端点。"""
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "ok")


if __name__ == "__main__":
    unittest.main()
