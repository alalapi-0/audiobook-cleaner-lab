#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LLM 机切建议 CLI。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from packages.llm_core.adapters.openai_compatible import OpenAiCompatibleAdapter  # noqa: E402
from packages.llm_core.service import LlmCutService  # noqa: E402


def _resolve_adapter(engine: str):
    if engine == "mock":
        return None
    if engine in ("openai", "openai_compatible", "real"):
        return OpenAiCompatibleAdapter()
    raise ValueError(f"未知 engine: {engine}（可选 mock / openai）")


def main() -> int:
    """CLI 入口。"""
    parser = argparse.ArgumentParser(description="audiobook-cleaner-lab LLM 机切建议")
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--chapter-id", required=True)
    parser.add_argument(
        "--engine",
        default="mock",
        choices=["mock", "openai", "openai_compatible", "real"],
        help="LLM 引擎：mock（默认）或 openai（真实 API）",
    )
    args = parser.parse_args()

    service = LlmCutService()
    try:
        adapter = _resolve_adapter(args.engine)
        result = service.run_llm_cut(args.project_id, args.chapter_id, adapter=adapter)
    except (FileNotFoundError, ValueError) as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1

    actions = {}
    for d in result.get("decisions", []):
        a = d.get("action", "unknown")
        actions[a] = actions.get(a, 0) + 1

    print(f"✓ LLM 机切建议完成: {args.chapter_id}")
    print(f"  engine: {result.get('llm_engine')}")
    print(f"  decisions: {len(result.get('decisions', []))}")
    print(f"  action 分布: {actions}")
    print(f"  output: {result.get('_output_path', '')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
