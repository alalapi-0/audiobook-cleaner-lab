#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FFmpeg 导出 CLI。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from packages.audio_core.export_service import ExportService  # noqa: E402


def main() -> int:
    """CLI 入口。"""
    parser = argparse.ArgumentParser(description="audiobook-cleaner-lab FFmpeg 导出")
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--chapter-id", required=True)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅输出 ffmpeg 命令，不写文件",
    )
    args = parser.parse_args()

    service = ExportService()
    try:
        result = service.export_chapter(
            args.project_id,
            args.chapter_id,
            dry_run=args.dry_run,
        )
    except FileNotFoundError as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1

    if not result.get("success"):
        print(f"错误: {result.get('error')}", file=sys.stderr)
        return 1

    mode = "dry-run" if args.dry_run else "正式导出"
    print(f"✓ {mode} 完成: {args.chapter_id}")
    print(f"  command: {result.get('ffmpeg_command', '')[:120]}...")
    print(f"  deleted_sec: {result.get('deleted_sec')}")
    if not args.dry_run:
        print(f"  output: {result.get('output_path')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
