#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""文本规范化 CLI。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from packages.text_core.service import TextNormalizationService  # noqa: E402


def main() -> int:
    """CLI 入口。"""
    parser = argparse.ArgumentParser(description="audiobook-cleaner-lab 文本规范化")
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--chapter-id", required=True)
    args = parser.parse_args()

    service = TextNormalizationService()
    try:
        result = service.normalize_chapter(args.project_id, args.chapter_id)
    except FileNotFoundError as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1

    print(f"✓ 文本规范化完成: {args.chapter_id}")
    print(f"  source: {result['normalized_source']}")
    print(f"  asr: {result['normalized_asr']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
