#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ASR 转写 CLI — mock 或导入 transcript。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from packages.asr_core.adapters import ImportTranscriptAdapter, MockAsrAdapter  # noqa: E402
from packages.asr_core.service import AsrService  # noqa: E402


def main() -> int:
    """CLI 入口。"""
    parser = argparse.ArgumentParser(description="audiobook-cleaner-lab ASR 转写")
    parser.add_argument("--project-id", required=True, help="项目 ID")
    parser.add_argument("--chapter-id", required=True, help="章节 ID")
    parser.add_argument(
        "--engine",
        choices=["mock", "import"],
        default="mock",
        help="ASR 引擎（mock 或 import）",
    )
    parser.add_argument(
        "--import-path",
        help="import 引擎时指定外部 transcript.json 路径",
    )
    args = parser.parse_args()

    if args.engine == "import":
        if not args.import_path:
            print("错误: import 引擎需要 --import-path", file=sys.stderr)
            return 1
        adapter = ImportTranscriptAdapter(args.import_path)
    else:
        adapter = MockAsrAdapter()

    service = AsrService()
    try:
        result = service.run_asr(args.project_id, args.chapter_id, adapter)
    except (FileNotFoundError, ValueError) as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1

    print(f"✓ ASR 完成: {args.chapter_id}")
    print(f"  engine: {result['asr_engine']}")
    print(f"  segments: {len(result['segments'])}")
    print(f"  output: {result.get('_output_path', result.get('artifacts', ''))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
