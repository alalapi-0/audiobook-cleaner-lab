#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Agent 自主验证门禁 — 组合仓库骨架、环境与前端 agent:check。"""

from __future__ import annotations

import compileall
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENV_PYTHON = ROOT / ".venv" / "bin" / "python"


def python_executable() -> str:
    """优先使用仓库 .venv 中的 Python（含 FastAPI 等项目依赖）。"""
    if VENV_PYTHON.is_file():
        return str(VENV_PYTHON)
    return sys.executable


def ensure_venv_python() -> None:
    """若存在 .venv 且当前非 venv 解释器，则用 venv 重新执行本脚本。"""
    if VENV_PYTHON.is_file() and Path(sys.executable).resolve() != VENV_PYTHON.resolve():
        os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), str(Path(__file__).resolve()), *sys.argv[1:]])

# Agent 相关配置与文档（MCP / Skill / Rule / 验证说明）
AGENT_ARTIFACTS = [
    ".cursor/mcp.json",
    ".cursor/skills/browser-debug-check/SKILL.md",
    ".cursor/rules/verification-gate.mdc",
    ".cursor/rules/mcp-agent-tools.mdc",
    "docs/agent-browser-verification.md",
    "docs/agent_skills/mcp_usage_skill.md",
    "scripts/check_mcp_config.py",
]

MCP_SERVER_NAMES = ("playwright", "chrome-devtools", "context7")


def run_script(name: str) -> int:
    """运行 scripts/ 下的 Python 脚本并返回 exit code。"""
    path = ROOT / "scripts" / name
    if not path.is_file():
        print(f"  ✗ 脚本缺失: scripts/{name}")
        return 1
    print(f"\n--- 运行 scripts/{name} ---")
    result = subprocess.run([python_executable(), str(path)], cwd=ROOT)
    return result.returncode


def check_agent_artifacts() -> list[str]:
    """检查 Agent MCP / Skill / Rule / 文档是否存在。"""
    issues: list[str] = []
    for rel in AGENT_ARTIFACTS:
        if not (ROOT / rel).is_file():
            issues.append(f"Agent 配置缺失: {rel}")
    return issues


def check_mcp_json() -> list[str]:
    """检查 .cursor/mcp.json 是否包含必需的 MCP server。"""
    issues: list[str] = []
    mcp_path = ROOT / ".cursor/mcp.json"
    if not mcp_path.is_file():
        return ["Agent 配置缺失: .cursor/mcp.json"]
    try:
        import json

        data = json.loads(mcp_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [f".cursor/mcp.json 无法解析: {exc}"]

    servers = data.get("mcpServers") or {}
    for name in MCP_SERVER_NAMES:
        if name not in servers:
            issues.append(f".cursor/mcp.json 缺少 MCP server: {name}")
    return issues


def compile_python() -> int:
    """编译 packages/ 与 apps/api 以捕获语法错误。"""
    print("\n--- Python compileall (packages/, apps/api/) ---")
    targets = [ROOT / "packages", ROOT / "apps" / "api"]
    ok = True
    for target in targets:
        if not target.is_dir():
            print(f"  ✗ 目录缺失: {target.relative_to(ROOT)}")
            ok = False
            continue
        if not compileall.compile_dir(str(target), quiet=1):
            ok = False
    if ok:
        print("  ✓ Python 编译检查通过")
        return 0
    print("  ✗ Python 编译检查失败")
    return 1


def run_npm_agent_check() -> int:
    """运行根目录 npm run agent:check（build + test）。"""
    pkg = ROOT / "package.json"
    if not pkg.is_file():
        print("  ✗ 根目录 package.json 缺失")
        return 1
    if not (ROOT / "apps" / "web" / "node_modules").is_dir():
        print("\n--- npm install (apps/web) ---")
        install = subprocess.run(
            ["npm", "install"],
            cwd=ROOT / "apps" / "web",
        )
        if install.returncode != 0:
            return install.returncode

    print("\n--- npm run agent:check ---")
    result = subprocess.run(["npm", "run", "agent:check"], cwd=ROOT)
    return result.returncode


def main() -> int:
    """执行 Agent 验证门禁。"""
    ensure_venv_python()
    print("=" * 50)
    print("audiobook-cleaner-lab Agent 验证门禁")
    print("=" * 50)

    issues: list[str] = []
    issues.extend(check_agent_artifacts())
    issues.extend(check_mcp_json())
    if issues:
        print("\nAgent 配置检查未通过：\n")
        for issue in issues:
            print(f"  ✗ {issue}")
        return 1
    print("\n✓ Agent MCP / Skill / Rule / 文档配置齐全")

    steps: list[tuple[str, int]] = []

    repo_code = run_script("check_repo.py")
    steps.append(("check_repo.py", repo_code))
    if repo_code != 0:
        print("\n门禁失败：仓库骨架检查未通过")
        return 1

    env_code = run_script("check_environment.py")
    steps.append(("check_environment.py", env_code))
    if env_code != 0:
        print("\n门禁失败：环境检查未通过")
        return 1

    py_code = compile_python()
    steps.append(("compileall", py_code))
    if py_code != 0:
        return 1

    npm_code = run_npm_agent_check()
    steps.append(("npm run agent:check", npm_code))
    if npm_code != 0:
        print("\n门禁失败：npm run agent:check 未通过")
        return 1

    print("\n" + "=" * 50)
    print("✓ Agent 验证门禁全部通过")
    for name, code in steps:
        print(f"  ✓ {name} (exit {code})")
    print("=" * 50)
    return 0


if __name__ == "__main__":
    sys.exit(main())
