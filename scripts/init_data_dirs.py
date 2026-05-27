#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""初始化本地 data 子目录 — 仅创建空目录与 .gitkeep，不写入真实素材。"""

from __future__ import annotations

import sys
from pathlib import Path

# 仓库根目录
ROOT = Path(__file__).resolve().parent.parent

# 需要创建的 data 子目录
DATA_SUBDIRS = [
    "data/raw_audio",
    "data/source_text",
    "data/transcripts",
    "data/normalized",
    "data/alignments",
    "data/cut_plans",
    "data/reviews",
    "data/exports",
    "data/waveforms",
    "data/logs",
]


def init_data_dirs() -> list[str]:
    """创建 data 子目录并在每个目录放置 .gitkeep。"""
    created: list[str] = []
    for rel in DATA_SUBDIRS:
        dir_path = ROOT / rel
        dir_path.mkdir(parents=True, exist_ok=True)
        gitkeep = dir_path / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.write_text("", encoding="utf-8")
            created.append(rel)
        else:
            created.append(f"{rel}（已存在）")
    return created


def main() -> int:
    """执行初始化并输出中文结果。"""
    print("=" * 50)
    print("audiobook-cleaner-lab data 目录初始化")
    print("=" * 50)
    print("\n正在创建 data 子目录...\n")

    results = init_data_dirs()
    for item in results:
        print(f"  ✓ {item}")

    print(f"\n共处理 {len(DATA_SUBDIRS)} 个子目录。")
    print("注意：本脚本不会写入真实音频或文本素材。")
    print("data 目录真实内容不应提交到 Git。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
