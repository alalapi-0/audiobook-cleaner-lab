#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LLM 机切建议单元测试。"""

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
from packages.alignment_core.service import AlignmentService  # noqa: E402
from packages.asr_core.adapters import MockAsrAdapter  # noqa: E402
from packages.asr_core.service import AsrService  # noqa: E402
from packages.llm_core.adapters.mock import MockLlmAdapter  # noqa: E402
from packages.llm_core.schemas.llm_cut_decision import (  # noqa: E402
    AUTO_DELETE_MIN_CONFIDENCE,
    LlmCutDecision,
)
from packages.llm_core.service import LlmCutService  # noqa: E402
from packages.text_core.service import TextNormalizationService  # noqa: E402


def _make_wav(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(b"\x00\x00" * 16000)


class TestMockLlmAdapter(unittest.TestCase):
    """MockLlmAdapter 规则测试。"""

    def test_matched_keep_extra_delete(self) -> None:
        """matched keep，extra_candidate delete。"""
        payload = {
            "chapter_id": "c1",
            "segments": [
                {
                    "segment_id": "seg_0001",
                    "start": 0.0,
                    "end": 4.0,
                    "alignment_status": "matched",
                    "filler_candidates": [],
                },
                {
                    "segment_id": "seg_0002",
                    "start": 4.0,
                    "end": 8.0,
                    "alignment_status": "extra_candidate",
                    "filler_candidates": [],
                },
            ],
        }
        result = MockLlmAdapter().decide(payload)
        decision = LlmCutDecision.from_dict(result)
        self.assertEqual(decision.validate(), [])

        by_id = {d.segment_id: d for d in decision.decisions}
        self.assertEqual(by_id["seg_0001"].action, "keep")
        self.assertEqual(by_id["seg_0002"].action, "delete")
        self.assertGreaterEqual(by_id["seg_0002"].confidence, AUTO_DELETE_MIN_CONFIDENCE)

    def test_low_confidence_not_delete(self) -> None:
        """低置信度不得 delete。"""
        payload = {
            "chapter_id": "c1",
            "segments": [
                {
                    "segment_id": "seg_0001",
                    "start": 0.0,
                    "end": 4.0,
                    "alignment_status": "low_similarity",
                    "filler_candidates": [],
                },
            ],
        }
        result = MockLlmAdapter().decide(payload)
        decision = LlmCutDecision.from_dict(result)
        self.assertEqual(decision.decisions[0].action, "uncertain")

    def test_uncertain_exists(self) -> None:
        """uncertain 条目存在。"""
        payload = {
            "chapter_id": "c1",
            "segments": [
                {
                    "segment_id": "seg_0001",
                    "start": 0.0,
                    "end": 4.0,
                    "alignment_status": "uncertain",
                    "filler_candidates": [],
                },
            ],
        }
        result = MockLlmAdapter().decide(payload)
        self.assertTrue(any(d["action"] == "uncertain" for d in result["decisions"]))


class TestLlmCutService(unittest.TestCase):
    """LlmCutService 集成测试。"""

    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tmpdir.name)
        self.manifest = ManifestService(root=self.root)
        self.asr = AsrService(root=self.root)
        self.norm = TextNormalizationService(root=self.root)
        self.align = AlignmentService(root=self.root)
        self.llm = LlmCutService(root=self.root)

        audio = self.root / "data/raw_audio/book_001/chapter_001.wav"
        text = self.root / "data/source_text/book_001/chapter_001.txt"
        _make_wav(audio)
        text.parent.mkdir(parents=True, exist_ok=True)
        text.write_text(
            "这是正确原文文本。后续段落内容。",
            encoding="utf-8",
        )

        self.manifest.create_project("book_001", "测试书")
        self.manifest.add_chapter(
            project_id="book_001",
            chapter_id="chapter_001",
            title="第一章",
            source_audio="data/raw_audio/book_001/chapter_001.wav",
            source_text="data/source_text/book_001/chapter_001.txt",
        )
        self.asr.run_asr("book_001", "chapter_001", MockAsrAdapter())
        self.norm.normalize_chapter("book_001", "chapter_001")
        self.align.align_chapter("book_001", "chapter_001")

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_run_llm_cut_writes_decision(self) -> None:
        """完整流水线生成 llm_cut_decision。"""
        result = self.llm.run_llm_cut("book_001", "chapter_001")
        chapter = self.manifest.load_chapter("book_001", "chapter_001")
        out_path = self.root / chapter.artifacts.llm_decision
        self.assertTrue(out_path.is_file())
        saved = json.loads(out_path.read_text(encoding="utf-8"))
        self.assertEqual(saved["llm_engine"], "mock")
        self.assertGreater(len(saved["decisions"]), 0)
        self.assertIn("decisions", result)


if __name__ == "__main__":
    unittest.main()
