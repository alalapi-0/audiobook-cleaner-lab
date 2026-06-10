#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""连续自动推进轮次入口 — 门禁、演示数据、验收摘要（不发起真实 LLM API）。"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENV_PYTHON = ROOT / ".venv" / "bin" / "python"
DEMO_MANIFEST = (
    ROOT / "data/projects/book_001/chapters/chapter_001/chapter_manifest.json"
)


def python_executable() -> str:
    if VENV_PYTHON.is_file():
        return str(VENV_PYTHON)
    return sys.executable


def ensure_venv_python() -> None:
    if VENV_PYTHON.is_file() and Path(sys.executable).resolve() != VENV_PYTHON.resolve():
        os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), str(Path(__file__).resolve()), *sys.argv[1:]])


def run(cmd: list[str], *, cwd: Path | None = None) -> int:
    print(f"\n$ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd or ROOT)
    return result.returncode


def seed_demo_if_needed(*, force: bool) -> int:
    if DEMO_MANIFEST.is_file() and not force:
        print(f"✓ 演示章节已存在: {DEMO_MANIFEST.relative_to(ROOT)}")
        return 0
    args = [python_executable(), str(ROOT / "scripts/seed_demo_chapter.py")]
    if force:
        args.append("--force")
    return run(args)


def main() -> int:
    ensure_venv_python()
    parser = argparse.ArgumentParser(description="audiobook-cleaner-lab 自动推进入口")
    parser.add_argument(
        "--skip-gate",
        action="store_true",
        help="跳过 agent_gate（仅 seed + check_repo）",
    )
    parser.add_argument(
        "--force-seed",
        action="store_true",
        help="强制重建 book_001/chapter_001 mock 数据",
    )
    parser.add_argument(
        "--round",
        type=int,
        default=0,
        help="日志用轮次编号（默认 0）",
    )
    args = parser.parse_args()

    print("=" * 50)
    print(f"audiobook-cleaner-lab 自动推进 (round={args.round})")
    print("=" * 50)

    run([python_executable(), str(ROOT / "scripts/init_data_dirs.py")])

    seed_code = seed_demo_if_needed(force=args.force_seed)
    if seed_code != 0:
        return seed_code

    if not args.skip_gate:
        gate_code = run([python_executable(), str(ROOT / "scripts/agent_gate.py")])
        if gate_code != 0:
            return gate_code
    else:
        repo_code = run([python_executable(), str(ROOT / "scripts/check_repo.py")])
        if repo_code != 0:
            return repo_code

    print("\n" + "=" * 50)
    print("✓ 自动推进验收通过（mock 模式）")
    print("  API:    http://127.0.0.1:8000/api/health")
    print(
        "  Review: http://localhost:5173/?project_id=book_001&chapter_id=chapter_001"
    )
    print("  启动:   bash scripts/start_local.sh")
    print("  真实 LLM: 配置 .env 后运行 scripts/real_api_check.py")
    print("=" * 50)
    return 0


if __name__ == "__main__":
    sys.exit(main())
