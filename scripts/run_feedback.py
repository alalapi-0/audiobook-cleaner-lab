#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""反馈分析 CLI。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from packages.feedback_core.service import FeedbackService  # noqa: E402


def main() -> int:
    """CLI 入口。"""
    parser = argparse.ArgumentParser(description="audiobook-cleaner-lab 反馈分析")
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--chapter-id", required=True)
    args = parser.parse_args()

    service = FeedbackService()
    try:
        result = service.generate_feedback(args.project_id, args.chapter_id)
    except FileNotFoundError as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1

    stats = result.get("stats", {})
    print(f"✓ 反馈记录已生成: {args.chapter_id}")
    print(f"  {result.get('summary', '')}")
    print(f"  误删风险: {stats.get('false_delete_risk', 0)}")
    print(f"  output: {result.get('_output_path', '')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
