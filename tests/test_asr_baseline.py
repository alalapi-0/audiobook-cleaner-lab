#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ASR 基线单元测试。"""

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
from packages.asr_core.adapters import ImportTranscriptAdapter, MockAsrAdapter  # noqa: E402
from packages.asr_core.schemas.transcript import Transcript  # noqa: E402
from packages.asr_core.service import AsrService  # noqa: E402


def _make_wav(path: Path, duration_sec: float = 2.0, rate: int = 16000) -> None:
    """创建最小 WAV 文件用于测试。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    n_frames = int(duration_sec * rate)
    with wave.open(str(path), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(b"\x00\x00" * n_frames)


class TestMockAsrAdapter(unittest.TestCase):
    """Mock ASR 测试。"""

    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tmpdir.name)
        self.audio = self.root / "test.wav"
        _make_wav(self.audio, duration_sec=8.0)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_mock_generates_valid_transcript(self) -> None:
        """mock 生成合法 transcript。"""
        adapter = MockAsrAdapter()
        data = adapter.transcribe(str(self.audio), "chapter_001", "book_001")
        transcript = Transcript.from_dict(data)
        self.assertEqual(transcript.validate(), [])
        self.assertEqual(transcript.asr_engine, "mock")
        self.assertGreaterEqual(len(transcript.segments), 3)
        for seg in transcript.segments:
            self.assertGreater(seg.end, seg.start)
            self.assertTrue(seg.text)


class TestImportTranscriptAdapter(unittest.TestCase):
    """Import ASR 测试。"""

    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tmpdir.name)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_import_validates_schema(self) -> None:
        """导入 transcript 校验 schema。"""
        import_path = self.root / "external.json"
        import_path.write_text(
            json.dumps(
                {
                    "chapter_id": "c1",
                    "project_id": "p1",
                    "asr_engine": "external",
                    "duration_sec": 10.0,
                    "segments": [
                        {
                            "segment_id": "seg_0001",
                            "start": 0.0,
                            "end": 5.0,
                            "text": "测试文本",
                            "confidence": 0.9,
                        }
                    ],
                    "created_at": "2026-01-01T00:00:00",
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        adapter = ImportTranscriptAdapter(str(import_path))
        data = adapter.transcribe("dummy.wav", "chapter_001", "book_001")
        self.assertEqual(data["chapter_id"], "chapter_001")
        self.assertEqual(len(data["segments"]), 1)


class TestAsrService(unittest.TestCase):
    """AsrService 集成测试。"""

    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tmpdir.name)
        self.manifest = ManifestService(root=self.root)
        self.asr = AsrService(root=self.root)

        audio = self.root / "data/raw_audio/book_001/chapter_001.wav"
        text = self.root / "data/source_text/book_001/chapter_001.txt"
        _make_wav(audio, duration_sec=12.0)
        text.parent.mkdir(parents=True, exist_ok=True)
        text.write_text("原文", encoding="utf-8")

        self.manifest.create_project("book_001", "测试书")
        self.manifest.add_chapter(
            project_id="book_001",
            chapter_id="chapter_001",
            title="第一章",
            source_audio="data/raw_audio/book_001/chapter_001.wav",
            source_text="data/source_text/book_001/chapter_001.txt",
        )

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_run_asr_updates_manifest(self) -> None:
        """run_asr 写入 transcript 并更新状态。"""
        result = self.asr.run_asr("book_001", "chapter_001", MockAsrAdapter())
        chapter = self.manifest.load_chapter("book_001", "chapter_001")
        self.assertEqual(chapter.status, "asr_done")
        transcript_path = self.root / chapter.artifacts.transcript
        self.assertTrue(transcript_path.is_file())
        saved = json.loads(transcript_path.read_text(encoding="utf-8"))
        self.assertEqual(saved["asr_engine"], "mock")
        self.assertEqual(len(result["segments"]), len(saved["segments"]))


if __name__ == "__main__":
    unittest.main()
