#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""本地环境检查 — Python、FFmpeg、Node。"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def check_python() -> tuple[bool, str]:
    """检查 Python 版本。"""
    v = sys.version_info
    ok = v >= (3, 10)
    return ok, f"Python {v.major}.{v.minor}.{v.micro}" + (" ✓" if ok else " ✗ 需要 >=3.10")


def check_ffmpeg() -> tuple[bool, str]:
    """检查 FFmpeg。"""
    path = shutil.which("ffmpeg")
    if not path:
        return False, "FFmpeg ✗ 未安装（Round 08 导出需要）"
    return True, f"FFmpeg ✓ ({path})"


def check_node() -> tuple[bool, str]:
    """检查 Node.js（前端可选）。"""
    path = shutil.which("node")
    if not path:
        return False, "Node.js ✗ 未安装（Round 06 前端需要）"
    import subprocess

    try:
        ver = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        ver = "unknown"
    return True, f"Node.js ✓ ({ver})"


def check_fastapi() -> tuple[bool, str]:
    """检查 FastAPI 是否可导入。"""
    try:
        import fastapi  # noqa: F401
        return True, "FastAPI ✓ 已安装"
    except ImportError:
        return False, "FastAPI ✗ 未安装（pip install fastapi uvicorn pydantic）"


def main() -> int:
    """执行环境检查。"""
    print("=" * 50)
    print("audiobook-cleaner-lab 环境检查")
    print("=" * 50)
    print(f"仓库根目录: {ROOT}\n")

    checks = [
        check_python(),
        check_ffmpeg(),
        check_node(),
        check_fastapi(),
    ]
    all_ok = True
    for ok, msg in checks:
        print(f"  {msg}")
        if not ok:
            all_ok = False

    print()
    if all_ok:
        print("✓ 环境检查通过，可运行本地流水线")
        return 0
    print("⚠ 部分依赖缺失，请按提示安装后重试")
    return 1


if __name__ == "__main__":
    sys.exit(main())
