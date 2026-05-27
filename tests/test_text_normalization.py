#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""文本规范化单元测试。"""

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
from packages.asr_core.adapters import MockAsrAdapter  # noqa: E402
from packages.asr_core.service import AsrService  # noqa: E402
from packages.text_core.filler_detector import detect_filler_candidates  # noqa: E402
from packages.text_core.normalizers import normalize_asr_segments, normalize_source_text  # noqa: E402
from packages.text_core.service import TextNormalizationService  # noqa: E402


def _make_wav(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(b"\x00\x00" * 16000)


class TestSourceNormalizer(unittest.TestCase):
    """原文清洗测试。"""

    def test_punctuation_and_whitespace(self) -> None:
        """标点统一与空格清理。"""
        raw = "  你好,世界!  \n\n  第二段.  "
        result = normalize_source_text(raw, "c1", "source.txt")
        self.assertIn("，", result["normalized_text"])
        self.assertIn("！", result["normalized_text"])
        self.assertIn("。", result["normalized_text"])
        self.assertNotIn("  ", result["normalized_text"])

    def test_heading_detection(self) -> None:
        """章节标题识别。"""
        raw = "第一章 开端\n正文内容。"
        result = normalize_source_text(raw, "c1", "source.txt")
        self.assertIn("heading_detect", result["rules_applied"])


class TestAsrNormalizer(unittest.TestCase):
    """ASR 清洗测试。"""

    def test_filler_marked_not_deleted(self) -> None:
        """filler 仅标记，auto_delete 为 false。"""
        transcript = {
            "chapter_id": "c1",
            "segments": [
                {"segment_id": "seg_0001", "text": "嗯，不对，我重新读"},
            ],
        }
        result = normalize_asr_segments(transcript)
        seg = result["segments"][0]
        self.assertTrue(seg["filler_candidates"])
        self.assertFalse(seg["filler_candidates"][0]["auto_delete"])

    def test_segment_id_preserved(self) -> None:
        """保留 segment_id 映射。"""
        transcript = {
            "chapter_id": "c1",
            "segments": [{"segment_id": "seg_0002", "text": "测试文本"}],
        }
        result = normalize_asr_segments(transcript)
        self.assertEqual(result["segments"][0]["segment_id"], "seg_0002")


class TestFillerDetector(unittest.TestCase):
    """filler_detector 测试。"""

    def test_sentence_initial_filler(self) -> None:
        """句首语气词标记为候选。"""
        cands = detect_filler_candidates("嗯不对")
        self.assertTrue(any(c["token"] == "嗯" for c in cands))

    def test_mid_sentence_not_filler(self) -> None:
        """句中合法用词不误标（保守策略：仅句首）。"""
        cands = detect_filler_candidates("他说然后就是")
        self.assertEqual(cands, [])


class TestTextNormalizationService(unittest.TestCase):
    """TextNormalizationService 集成测试。"""

    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tmpdir.name)
        self.manifest = ManifestService(root=self.root)
        self.asr = AsrService(root=self.root)
        self.norm = TextNormalizationService(root=self.root)

        audio = self.root / "data/raw_audio/book_001/chapter_001.wav"
        text = self.root / "data/source_text/book_001/chapter_001.txt"
        _make_wav(audio)
        text.parent.mkdir(parents=True, exist_ok=True)
        text.write_text("第一章 测试\n你好,世界!", encoding="utf-8")

        self.manifest.create_project("book_001", "测试书")
        self.manifest.add_chapter(
            project_id="book_001",
            chapter_id="chapter_001",
            title="第一章",
            source_audio="data/raw_audio/book_001/chapter_001.wav",
            source_text="data/source_text/book_001/chapter_001.txt",
        )
        self.asr.run_asr("book_001", "chapter_001", MockAsrAdapter())

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_normalize_chapter_writes_artifacts(self) -> None:
        """规范化写入 normalized 产物。"""
        result = self.norm.normalize_chapter("book_001", "chapter_001")
        source_path = self.root / result["normalized_source"]
        asr_path = self.root / result["normalized_asr"]
        self.assertTrue(source_path.is_file())
        self.assertTrue(asr_path.is_file())
        asr_data = json.loads(asr_path.read_text(encoding="utf-8"))
        self.assertIn("segments", asr_data)
        self.assertIn("filler_detect", asr_data["rules_applied"])


if __name__ == "__main__":
    unittest.main()
