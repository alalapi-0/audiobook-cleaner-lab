#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""对齐 CLI。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from packages.alignment_core.service import AlignmentService  # noqa: E402


def main() -> int:
    """CLI 入口。"""
    parser = argparse.ArgumentParser(description="audiobook-cleaner-lab 原文与 ASR 对齐")
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--chapter-id", required=True)
    args = parser.parse_args()

    service = AlignmentService()
    try:
        result = service.align_chapter(args.project_id, args.chapter_id)
    except (FileNotFoundError, ValueError) as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1

    statuses = {}
    for item in result.get("items", []):
        s = item.get("status", "unknown")
        statuses[s] = statuses.get(s, 0) + 1

    print(f"✓ 对齐完成: {args.chapter_id}")
    print(f"  items: {len(result.get('items', []))}")
    print(f"  status 分布: {statuses}")
    print(f"  output: {result.get('_output_path', '')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
