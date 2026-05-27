#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""素材导入 CLI — 创建项目与章节 manifest。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# 确保仓库根目录在 sys.path 中
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.api.services.manifest_service import ManifestError, ManifestService  # noqa: E402


def cmd_create_project(args: argparse.Namespace) -> int:
    """创建书籍项目。"""
    service = ManifestService()
    try:
        manifest = service.create_project(
            project_id=args.project_id,
            book_title=args.title,
            language=args.language,
        )
    except ManifestError as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1

    path = service.project_manifest_path(args.project_id)
    print(f"✓ 已创建项目: {manifest.project_id}")
    print(f"  manifest: {path.relative_to(ROOT)}")
    return 0


def cmd_add_chapter(args: argparse.Namespace) -> int:
    """向项目添加章节。"""
    service = ManifestService()
    try:
        chapter = service.add_chapter(
            project_id=args.project_id,
            chapter_id=args.chapter_id,
            title=args.title,
            source_audio=args.audio,
            source_text=args.text,
            order=args.order,
            validate_paths=not args.skip_path_check,
        )
    except ManifestError as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1

    path = service.chapter_manifest_path(args.project_id, args.chapter_id)
    print(f"✓ 已添加章节: {chapter.chapter_id}")
    print(f"  manifest: {path.relative_to(ROOT)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。"""
    parser = argparse.ArgumentParser(
        description="audiobook-cleaner-lab 素材导入 — 生成 project/chapter manifest",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    create = sub.add_parser("create-project", help="创建书籍项目")
    create.add_argument("--project-id", required=True, help="项目 ID，如 book_001")
    create.add_argument("--title", required=True, help="书名")
    create.add_argument("--language", default="zh-CN", help="语言代码")
    create.set_defaults(func=cmd_create_project)

    add = sub.add_parser("add-chapter", help="添加章节并登记素材路径")
    add.add_argument("--project-id", required=True, help="项目 ID")
    add.add_argument("--chapter-id", required=True, help="章节 ID")
    add.add_argument("--title", required=True, help="章节标题")
    add.add_argument("--audio", required=True, help="原始音频相对路径")
    add.add_argument("--text", required=True, help="原文文本相对路径")
    add.add_argument("--order", type=int, default=None, help="章节顺序")
    add.add_argument(
        "--skip-path-check",
        action="store_true",
        help="跳过音频/原文路径存在性校验（仅测试用）",
    )
    add.set_defaults(func=cmd_add_chapter)

    return parser


def main() -> int:
    """CLI 入口。"""
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
