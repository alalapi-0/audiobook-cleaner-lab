#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Manifest schema 与导入服务单元测试。"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.api.schemas.manifest import (  # noqa: E402
    ChapterArtifacts,
    ChapterManifest,
    ChapterStatus,
    ChapterSummary,
    ProjectDefaults,
    ProjectManifest,
)
from apps.api.services.manifest_service import ManifestError, ManifestService  # noqa: E402


class TestManifestSchema(unittest.TestCase):
    """Manifest schema 校验测试。"""

    def test_project_manifest_roundtrip(self) -> None:
        """project_manifest 序列化往返。"""
        manifest = ProjectManifest(
            project_id="book_001",
            book_title="示例有声书",
            language="zh-CN",
            created_at="2026-01-01T00:00:00",
            updated_at="2026-01-01T00:00:00",
            chapters=[
                ChapterSummary(
                    chapter_id="chapter_001",
                    title="第一章",
                    status=ChapterStatus.IMPORTED.value,
                    order=1,
                )
            ],
            defaults=ProjectDefaults(),
        )
        self.assertEqual(manifest.validate(), [])
        restored = ProjectManifest.from_dict(manifest.to_dict())
        self.assertEqual(restored.project_id, "book_001")
        self.assertEqual(len(restored.chapters), 1)

    def test_chapter_manifest_artifacts_paths(self) -> None:
        """chapter_manifest 默认产物路径符合 DATA_MODEL。"""
        artifacts = ChapterArtifacts.default_paths("book_001", "chapter_001")
        self.assertIn("data/transcripts/book_001/chapter_001.json", artifacts.transcript)
        self.assertIn("data/exports/book_001/chapter_001_clean.mp3", artifacts.export)

    def test_invalid_status_rejected(self) -> None:
        """非法 status 应被拒绝。"""
        chapter = ChapterManifest(
            chapter_id="c1",
            project_id="p1",
            title="t",
            source_audio="a.wav",
            source_text="a.txt",
            status="invalid",
            artifacts=ChapterArtifacts.default_paths("p1", "c1"),
            created_at="2026-01-01T00:00:00",
        )
        errors = chapter.validate()
        self.assertTrue(any("status" in e for e in errors))


class TestManifestService(unittest.TestCase):
    """ManifestService 集成测试（临时目录）。"""

    def setUp(self) -> None:
        """创建临时工作区。"""
        self._tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tmpdir.name)
        self.service = ManifestService(root=self.root)

        # 模拟素材文件
        audio = self.root / "data/raw_audio/book_001/chapter_001.wav"
        text = self.root / "data/source_text/book_001/chapter_001.txt"
        audio.parent.mkdir(parents=True, exist_ok=True)
        text.parent.mkdir(parents=True, exist_ok=True)
        audio.write_bytes(b"RIFF")
        text.write_text("示例原文", encoding="utf-8")

    def tearDown(self) -> None:
        """清理临时目录。"""
        self._tmpdir.cleanup()

    def test_create_project_and_add_chapter(self) -> None:
        """创建项目并添加章节。"""
        self.service.create_project("book_001", "测试书")
        chapter = self.service.add_chapter(
            project_id="book_001",
            chapter_id="chapter_001",
            title="第一章",
            source_audio="data/raw_audio/book_001/chapter_001.wav",
            source_text="data/source_text/book_001/chapter_001.txt",
        )

        project_path = self.service.project_manifest_path("book_001")
        chapter_path = self.service.chapter_manifest_path("book_001", "chapter_001")
        self.assertTrue(project_path.is_file())
        self.assertTrue(chapter_path.is_file())

        project = self.service.load_project("book_001")
        self.assertEqual(len(project.chapters), 1)
        self.assertEqual(chapter.status, ChapterStatus.IMPORTED.value)

        loaded = self.service.load_chapter("book_001", "chapter_001")
        self.assertEqual(loaded.chapter_id, "chapter_001")

    def test_missing_audio_raises(self) -> None:
        """音频不存在时应报错。"""
        self.service.create_project("book_001", "测试书")
        with self.assertRaises(ManifestError) as ctx:
            self.service.add_chapter(
                project_id="book_001",
                chapter_id="chapter_002",
                title="第二章",
                source_audio="data/raw_audio/missing.wav",
                source_text="data/source_text/book_001/chapter_001.txt",
            )
        self.assertIn("音频文件不存在", str(ctx.exception))

    def test_manifest_json_structure(self) -> None:
        """写入的 JSON 包含 DATA_MODEL 必需字段。"""
        self.service.create_project("book_001", "测试书")
        self.service.add_chapter(
            project_id="book_001",
            chapter_id="chapter_001",
            title="第一章",
            source_audio="data/raw_audio/book_001/chapter_001.wav",
            source_text="data/source_text/book_001/chapter_001.txt",
        )

        project_data = json.loads(
            self.service.project_manifest_path("book_001").read_text(encoding="utf-8")
        )
        self.assertIn("defaults", project_data)
        self.assertIn("chapters", project_data)

        chapter_data = json.loads(
            self.service.chapter_manifest_path("book_001", "chapter_001").read_text(
                encoding="utf-8"
            )
        )
        self.assertIn("artifacts", chapter_data)
        self.assertIn("transcript", chapter_data["artifacts"])


if __name__ == "__main__":
    unittest.main()
