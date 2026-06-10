#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Agent 自主验证门禁 — 组合仓库骨架、Agent Layer 文件、环境与前端 agent:check。

输出 reports/gate_result.json；不自动 commit/push，不真实调用付费 API。
"""

from __future__ import annotations

import compileall
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENV_PYTHON = ROOT / ".venv" / "bin" / "python"
GATE_RESULT_PATH = ROOT / "reports" / "gate_result.json"

AGENT_LAYER_FILES = [
    "AGENTS.md",
    "agent_layer.yaml",
    "agent_tools.yaml",
    "docs/TOOL_USAGE_POLICY.md",
    "docs/AGENT_RUNBOOK.md",
    "docs/AGENT_ROADMAP.md",
    "docs/SEARCH_POLICY.md",
    "schemas/agent_round_report.schema.json",
]

AGENT_ARTIFACTS = [
    ".cursor/mcp.json",
    ".cursor/skills/browser-debug-check/SKILL.md",
    ".cursor/rules/verification-gate.mdc",
    ".cursor/rules/mcp-agent-tools.mdc",
    "docs/agent-browser-verification.md",
    "docs/agent_skills/mcp_usage_skill.md",
    "scripts/check_mcp_config.py",
]

MCP_SERVER_NAMES = ("playwright", "chrome-devtools", "context7", "filesystem", "github", "stitch")


def python_executable() -> str:
    if VENV_PYTHON.is_file():
        return str(VENV_PYTHON)
    return sys.executable


def ensure_venv_python() -> None:
    if VENV_PYTHON.is_file() and Path(sys.executable).resolve() != VENV_PYTHON.resolve():
        os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), str(Path(__file__).resolve()), *sys.argv[1:]])


def run_script(name: str) -> tuple[int, str]:
    path = ROOT / "scripts" / name
    if not path.is_file():
        return 1, f"脚本缺失: scripts/{name}"
    print(f"\n--- 运行 scripts/{name} ---")
    result = subprocess.run([python_executable(), str(path)], cwd=ROOT)
    summary = "passed" if result.returncode == 0 else f"exit {result.returncode}"
    return result.returncode, summary


def check_files(rel_paths: list[str], label: str) -> tuple[list[str], list[str]]:
    passed: list[str] = []
    failed: list[str] = []
    for rel in rel_paths:
        if (ROOT / rel).is_file():
            passed.append(f"{label}: {rel}")
        else:
            failed.append(f"{label} 缺失: {rel}")
    return passed, failed


def check_mcp_json() -> list[str]:
    issues: list[str] = []
    mcp_path = ROOT / ".cursor" / "mcp.json"
    if not mcp_path.is_file():
        return ["Agent 配置缺失: .cursor/mcp.json"]
    try:
        data = json.loads(mcp_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [f".cursor/mcp.json 无法解析: {exc}"]
    servers = data.get("mcpServers") or {}
    for name in MCP_SERVER_NAMES:
        if name not in servers:
            issues.append(f".cursor/mcp.json 缺少 MCP server: {name}")
    return issues


def compile_python() -> tuple[int, str]:
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
        return 0, "passed"
    return 1, "compile failed"


def run_pytest() -> tuple[int, str]:
    tests_dir = ROOT / "tests"
    if not tests_dir.is_dir():
        return 0, "skipped: no tests/"
    import importlib.util

    if importlib.util.find_spec("pytest") is None:
        return 0, "skipped: pytest not installed in venv"
    print("\n--- pytest tests/ ---")
    result = subprocess.run(
        [python_executable(), "-m", "pytest", "tests/", "-q"],
        cwd=ROOT,
    )
    summary = "passed" if result.returncode == 0 else "tests failed"
    return result.returncode, summary


def run_npm_agent_check() -> tuple[int, str]:
    pkg = ROOT / "package.json"
    if not pkg.is_file():
        return 1, "根目录 package.json 缺失"
    if not (ROOT / "apps" / "web" / "node_modules").is_dir():
        print("\n--- npm install (apps/web) ---")
        install = subprocess.run(["npm", "install"], cwd=ROOT / "apps" / "web")
        if install.returncode != 0:
            return install.returncode, "npm install failed"
    print("\n--- npm run agent:check ---")
    result = subprocess.run(["npm", "run", "agent:check"], cwd=ROOT)
    summary = "passed" if result.returncode == 0 else "agent:check failed"
    return result.returncode, summary


def write_gate_result(payload: dict) -> None:
    GATE_RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    GATE_RESULT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    ensure_venv_python()
    timestamp = datetime.now(timezone.utc).isoformat()
    print("=" * 50)
    print("audiobook-cleaner-lab Agent 验证门禁")
    print("=" * 50)

    passed: list[str] = []
    failed: list[str] = []
    skipped: list[str] = []
    blocked: list[str] = []
    commands: list[dict] = []
    tool_usage = [
        {"tool": "shell", "used": True, "purpose": "run gates"},
        {"tool": "web_search", "used": False, "reason": "gate script only"},
        {"tool": "playwright_mcp", "used": False, "reason": "CLI playwright via npm test instead"},
    ]

    p_layer, f_layer = check_files(AGENT_LAYER_FILES, "agent_layer")
    passed.extend(p_layer)
    failed.extend(f_layer)

    p_art, f_art = check_files(AGENT_ARTIFACTS, "artifact")
    passed.extend(p_art)
    failed.extend(f_art)

    mcp_issues = check_mcp_json()
    if mcp_issues:
        failed.extend(mcp_issues)
    else:
        passed.append("mcp.json: all required servers present")

    if failed:
        print("\nAgent Layer / 配置检查未通过：\n")
        for issue in failed:
            print(f"  ✗ {issue}")
        write_gate_result(
            {
                "status": "failed",
                "timestamp": timestamp,
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "blocked": blocked,
                "commands": commands,
                "tool_usage": tool_usage,
                "next_action": "fix_missing_agent_layer_files",
            }
        )
        return 1

    print("\n✓ Agent Layer 与 MCP 配置文件齐全")

    step_defs = [
        ("check_repo.py", lambda: run_script("check_repo.py")),
        ("check_environment.py", lambda: run_script("check_environment.py")),
        ("compileall", compile_python),
        ("pytest", run_pytest),
        ("npm run agent:check", run_npm_agent_check),
    ]

    overall_ok = True
    for name, fn in step_defs:
        code, summary = fn()
        commands.append({"name": name, "command": name, "exit_code": code, "summary": summary})
        if "skipped" in summary:
            skipped.append(f"{name}: {summary}")
            if code != 0:
                overall_ok = False
        elif code == 0:
            passed.append(name)
        else:
            failed.append(name)
            overall_ok = False
            if name in ("check_repo.py", "check_environment.py"):
                break

    status = "passed" if overall_ok else "failed"
    next_action = "continue_next_round" if overall_ok else "fix_failed_tests"

    write_gate_result(
        {
            "status": status,
            "timestamp": timestamp,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "blocked": blocked,
            "commands": commands,
            "tool_usage": tool_usage,
            "next_action": next_action,
        }
    )

    print(f"\n门禁结果: {status}")
    print(f"报告: {GATE_RESULT_PATH.relative_to(ROOT)}")
    print("=" * 50)
    return 0 if overall_ok else 1


if __name__ == "__main__":
    sys.exit(main())
