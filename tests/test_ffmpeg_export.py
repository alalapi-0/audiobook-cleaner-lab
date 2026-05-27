#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FFmpeg 导出单元测试。"""

from __future__ import annotations

import json
import shutil
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
from packages.audio_core.export_service import ExportService  # noqa: E402
from packages.audio_core.ffmpeg_exporter import FfmpegExporter  # noqa: E402
from packages.llm_core.service import LlmCutService  # noqa: E402
from packages.text_core.service import TextNormalizationService  # noqa: E402


def _make_wav(path: Path, duration_sec: float = 3.0, rate: int = 16000) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    n = int(duration_sec * rate)
    with wave.open(str(path), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(b"\x00\x01" * n)


class TestFfmpegExporter(unittest.TestCase):
    """FfmpegExporter 测试。"""

    def setUp(self) -> None:
        if not shutil.which("ffmpeg"):
            self.skipTest("FFmpeg 未安装")
        self._tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tmpdir.name)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_dry_run_command(self) -> None:
        """dry-run 生成正确 ffmpeg 命令。"""
        audio = self.root / "data/raw_audio/test/ch.wav"
        _make_wav(audio, duration_sec=5.0)
        cut_plan = {
            "source_audio": "data/raw_audio/test/ch.wav",
            "delete_ranges": [{"start": 1.0, "end": 2.0}],
            "export": {
                "format": "wav",
                "output_path": "data/exports/test/ch_clean.wav",
            },
        }
        exporter = FfmpegExporter()
        result = exporter.export(cut_plan, self.root, dry_run=True)
        self.assertTrue(result.success)
        self.assertIn("aselect", result.command)
        self.assertAlmostEqual(result.deleted_sec, 1.0)

    def test_real_export_wav(self) -> None:
        """正式导出 WAV 文件。"""
        audio = self.root / "data/raw_audio/test/ch.wav"
        _make_wav(audio, duration_sec=4.0)
        out = self.root / "data/exports/test/ch_clean.wav"
        cut_plan = {
            "source_audio": "data/raw_audio/test/ch.wav",
            "delete_ranges": [{"start": 1.0, "end": 2.0}],
            "export": {
                "format": "wav",
                "output_path": "data/exports/test/ch_clean.wav",
            },
        }
        exporter = FfmpegExporter()
        result = exporter.export(cut_plan, self.root, dry_run=False)
        self.assertTrue(result.success, result.error)
        self.assertTrue(out.is_file())
        self.assertAlmostEqual(result.deleted_sec, 1.0)
        self.assertGreater(result.input_duration_sec, 0)


class TestExportService(unittest.TestCase):
    """ExportService 集成测试。"""

    def setUp(self) -> None:
        if not shutil.which("ffmpeg"):
            self.skipTest("FFmpeg 未安装")
        self._tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tmpdir.name)
        self._run_pipeline()

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def _run_pipeline(self) -> None:
        manifest = ManifestService(root=self.root)
        asr = AsrService(root=self.root)
        norm = TextNormalizationService(root=self.root)
        align = AlignmentService(root=self.root)
        llm = LlmCutService(root=self.root)
        review = ReviewService(root=self.root)

        audio = self.root / "data/raw_audio/book_001/chapter_001.wav"
        text = self.root / "data/source_text/book_001/chapter_001.txt"
        _make_wav(audio, duration_sec=6.0)
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

        data = review.get_review_data("book_001", "chapter_001")
        decisions = [
            {
                "segment_id": s["segment_id"],
                "user_action": s.get("model_action", "keep"),
                "user_adjusted_cut": s.get("suggested_cut"),
            }
            for s in data["segments"]
        ]
        review.save_review("book_001", "chapter_001", decisions)

        # 覆盖 export 为 wav 便于测试
        chapter = manifest.load_chapter("book_001", "chapter_001")
        cut_plan_path = self.root / chapter.artifacts.cut_plan
        cp = json.loads(cut_plan_path.read_text(encoding="utf-8"))
        cp["export"] = {
            "format": "wav",
            "output_path": "data/exports/book_001/chapter_001_clean.wav",
        }
        cut_plan_path.write_text(json.dumps(cp, ensure_ascii=False, indent=2), encoding="utf-8")

    def test_export_dry_run_and_real(self) -> None:
        """流水线后 dry-run 与正式导出。"""
        export = ExportService(root=self.root)
        dry = export.export_chapter("book_001", "chapter_001", dry_run=True)
        self.assertTrue(dry["success"])
        self.assertIn("ffmpeg", dry["ffmpeg_command"])

        real = export.export_chapter("book_001", "chapter_001", dry_run=False)
        self.assertTrue(real["success"])
        chapter = ManifestService(root=self.root).load_chapter("book_001", "chapter_001")
        self.assertEqual(chapter.status, "exported")


if __name__ == "__main__":
    unittest.main()
