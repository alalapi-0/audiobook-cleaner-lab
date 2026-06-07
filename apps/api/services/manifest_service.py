# -*- coding: utf-8 -*-
"""Manifest 读写与项目/章节导入服务。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apps.api.schemas.manifest import (
    ChapterArtifacts,
    ChapterManifest,
    ChapterStatus,
    ChapterSummary,
    ProjectManifest,
    iso_now,
)

# 仓库根目录（apps/api/services 上三级）
ROOT = Path(__file__).resolve().parents[3]


class ManifestError(Exception):
    """Manifest 操作错误。"""


class ManifestService:
    """书籍项目与章节 manifest 管理。"""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or ROOT

    def project_dir(self, project_id: str) -> Path:
        """项目数据目录。"""
        return self.root / "data" / "projects" / project_id

    def project_manifest_path(self, project_id: str) -> Path:
        """project_manifest.json 路径。"""
        return self.project_dir(project_id) / "project_manifest.json"

    def chapter_manifest_path(self, project_id: str, chapter_id: str) -> Path:
        """chapter_manifest.json 路径。"""
        return (
            self.project_dir(project_id)
            / "chapters"
            / chapter_id
            / "chapter_manifest.json"
        )

    def _resolve_path(self, rel_path: str) -> Path:
        """将相对路径解析为绝对路径。"""
        path = Path(rel_path)
        if path.is_absolute():
            return path
        return self.root / path

    def _display_path(self, path: Path) -> str:
        """错误信息中使用的仓库相对路径，避免暴露本机绝对路径。"""
        try:
            return str(path.relative_to(self.root))
        except ValueError:
            return path.name

    def _validate_source_paths(self, source_audio: str, source_text: str) -> None:
        """校验音频与原文路径存在（不读取文件内容）。"""
        audio_path = self._resolve_path(source_audio)
        text_path = self._resolve_path(source_text)
        if not audio_path.is_file():
            raise ManifestError(f"音频文件不存在: {source_audio}")
        if not text_path.is_file():
            raise ManifestError(f"原文文件不存在: {source_text}")

    def _write_json(self, path: Path, data: dict[str, Any]) -> None:
        """写入 JSON 文件。"""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def _read_json(self, path: Path) -> dict[str, Any]:
        """读取 JSON 文件。"""
        if not path.is_file():
            raise ManifestError(f"manifest 不存在: {self._display_path(path)}")
        return json.loads(path.read_text(encoding="utf-8"))

    def create_project(
        self,
        project_id: str,
        book_title: str,
        language: str = "zh-CN",
    ) -> ProjectManifest:
        """创建书籍项目并写入 project_manifest.json。"""
        manifest_path = self.project_manifest_path(project_id)
        if manifest_path.exists():
            raise ManifestError(f"项目已存在: {project_id}")

        now = iso_now()
        manifest = ProjectManifest(
            project_id=project_id,
            book_title=book_title,
            language=language,
            created_at=now,
            updated_at=now,
            chapters=[],
        )
        errors = manifest.validate()
        if errors:
            raise ManifestError("; ".join(errors))

        self._write_json(manifest_path, manifest.to_dict())
        return manifest

    def load_project(self, project_id: str) -> ProjectManifest:
        """加载 project_manifest.json。"""
        data = self._read_json(self.project_manifest_path(project_id))
        manifest = ProjectManifest.from_dict(data)
        errors = manifest.validate()
        if errors:
            raise ManifestError(f"project_manifest 校验失败: {'; '.join(errors)}")
        return manifest

    def add_chapter(
        self,
        project_id: str,
        chapter_id: str,
        title: str,
        source_audio: str,
        source_text: str,
        order: int | None = None,
        validate_paths: bool = True,
    ) -> ChapterManifest:
        """向项目添加章节并写入 chapter_manifest.json。"""
        project = self.load_project(project_id)

        if any(c.chapter_id == chapter_id for c in project.chapters):
            raise ManifestError(f"章节已存在: {chapter_id}")

        if validate_paths:
            self._validate_source_paths(source_audio, source_text)

        if order is None:
            order = len(project.chapters) + 1

        chapter = ChapterManifest(
            chapter_id=chapter_id,
            project_id=project_id,
            title=title,
            source_audio=source_audio,
            source_text=source_text,
            status=ChapterStatus.IMPORTED.value,
            artifacts=ChapterArtifacts.default_paths(project_id, chapter_id),
            created_at=iso_now(),
        )
        errors = chapter.validate()
        if errors:
            raise ManifestError("; ".join(errors))

        chapter_path = self.chapter_manifest_path(project_id, chapter_id)
        self._write_json(chapter_path, chapter.to_dict())

        project.chapters.append(
            ChapterSummary(
                chapter_id=chapter_id,
                title=title,
                status=ChapterStatus.IMPORTED.value,
                order=order,
            )
        )
        project.updated_at = iso_now()
        self._write_json(
            self.project_manifest_path(project_id),
            project.to_dict(),
        )
        return chapter

    def load_chapter(self, project_id: str, chapter_id: str) -> ChapterManifest:
        """加载 chapter_manifest.json。"""
        data = self._read_json(self.chapter_manifest_path(project_id, chapter_id))
        chapter = ChapterManifest.from_dict(data)
        errors = chapter.validate()
        if errors:
            raise ManifestError(f"chapter_manifest 校验失败: {'; '.join(errors)}")
        return chapter
