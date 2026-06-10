#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""轻量只读工具探针 — 生成 reports/tool_probe_report.json。

用法:
  python3 scripts/tool_probe.py          # 本地盘点，始终 exit 0
  python3 scripts/tool_probe.py --ci     # CI/pre-commit：必需工具缺失则 exit 1
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORT_PATH = ROOT / "reports" / "tool_probe_report.json"

REQUIRED_BINARIES = ("git", "node", "npm", "python3")
OPTIONAL_BINARIES = ("uv", "ffmpeg", "gh", "docker", "make", "java")

MCP_SERVERS = [
    "playwright",
    "chrome-devtools",
    "context7",
    "filesystem",
    "github",
    "stitch",
]


def run_cmd(cmd: list[str], timeout: int = 30) -> dict:
    """运行只读命令并返回探针结果。"""
    try:
        result = subprocess.run(
            cmd,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        out = (result.stdout or "") + (result.stderr or "")
        summary = out.strip().split("\n")[0] if out.strip() else ""
        return {
            "command": " ".join(cmd),
            "exit_code": result.returncode,
            "available": result.returncode == 0,
            "summary": summary[:200],
        }
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as exc:
        return {
            "command": " ".join(cmd),
            "exit_code": -1,
            "available": False,
            "summary": str(exc),
        }


def probe_binary(name: str, version_args: list[str] | None = None) -> dict:
    """检查二进制是否在 PATH 中。"""
    path = shutil.which(name)
    if not path:
        return {"name": name, "available": False, "path": None, "summary": "not in PATH"}
    if version_args:
        probe = run_cmd([name, *version_args])
        return {
            "name": name,
            "available": probe["available"],
            "path": path,
            "summary": probe["summary"],
        }
    return {"name": name, "available": True, "path": path, "summary": path}


def probe_mcp_config() -> dict:
    """检查 .cursor/mcp.json 配置（不调用 MCP 服务器）。"""
    mcp_path = ROOT / ".cursor" / "mcp.json"
    if not mcp_path.is_file():
        return {"configured": False, "servers": {}, "missing": MCP_SERVERS}
    try:
        data = json.loads(mcp_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {"configured": False, "error": str(exc)}
    servers = data.get("mcpServers") or {}
    result = {}
    for name in MCP_SERVERS:
        result[name] = {
            "configured": name in servers,
            "callable_now": "unknown",
            "note": "MCP 是否在当前 Agent 线程可调用需在对话中确认",
        }
    return {"configured": True, "servers": result}


def probe_cursor_rules() -> dict:
    """列出 .cursor/rules 与 skills。"""
    rules_dir = ROOT / ".cursor" / "rules"
    skills_dir = ROOT / ".cursor" / "skills"
    rules = sorted(rules_dir.glob("*")) if rules_dir.is_dir() else []
    skills = sorted(skills_dir.rglob("SKILL.md")) if skills_dir.is_dir() else []
    return {
        "rules_count": len(rules),
        "rules": [p.name for p in rules],
        "skills_count": len(skills),
        "skills": [str(p.relative_to(ROOT)) for p in skills],
    }


def evaluate_ci_status(binaries: list[dict], cmd_probes: list[dict]) -> dict:
    """在 --ci 模式下评估必需/可选工具与命令探针。"""
    by_name = {b["name"]: b for b in binaries}
    missing_required = [name for name in REQUIRED_BINARIES if not by_name.get(name, {}).get("available")]
    blocked_env = [name for name in OPTIONAL_BINARIES if not by_name.get(name, {}).get("available")]

    mcp_check = next((p for p in cmd_probes if "check:mcp" in p.get("command", "")), None)
    mcp_ok = mcp_check is None or mcp_check.get("available")

    if missing_required or not mcp_ok:
        status = "failed"
    elif blocked_env:
        status = "partial"
    else:
        status = "passed"

    return {
        "mode": "ci",
        "status": status,
        "missing_required": missing_required,
        "blocked_env": blocked_env,
        "mcp_config_check_ok": mcp_ok,
    }


def main() -> int:
    """执行探针并写入 JSON 报告。"""
    parser = argparse.ArgumentParser(description="audiobook-cleaner-lab 工具探针")
    parser.add_argument(
        "--ci",
        action="store_true",
        help="CI/pre-commit 模式：必需工具或 check:mcp 失败时 exit 1",
    )
    args = parser.parse_args()

    timestamp = datetime.now(timezone.utc).isoformat()
    print("=" * 50)
    print("audiobook-cleaner-lab 工具探针")
    if args.ci:
        print("模式: CI / pre-commit")
    print("=" * 50)

    binaries = [
        probe_binary("git"),
        probe_binary("node", ["-v"]),
        probe_binary("npm", ["-v"]),
        probe_binary("python3", ["--version"]),
        probe_binary("uv", ["--version"]),
        probe_binary("ffmpeg", ["-version"]),
        probe_binary("gh", ["--version"]),
        probe_binary("docker", ["--version"]),
        probe_binary("make", ["--version"]),
        probe_binary("java", ["-version"]),
    ]

    cmd_probes = [
        run_cmd(["git", "branch", "--show-current"]),
        run_cmd(["git", "status", "--short"]),
        run_cmd(["npm", "run", "check:mcp"], timeout=60),
    ]

    web_dir = ROOT / "apps" / "web"
    if (web_dir / "node_modules").is_dir():
        cmd_probes.append(run_cmd(["npx", "playwright", "--version"], timeout=60))
    else:
        cmd_probes.append(
            {
                "command": "npx playwright --version",
                "exit_code": -1,
                "available": False,
                "summary": "skipped: apps/web/node_modules missing",
            }
        )

    report = {
        "timestamp": timestamp,
        "repo": "audiobook-cleaner-lab",
        "cwd": str(ROOT),
        "agent_surface": "cursor",
        "curator_note": "callable_now for MCP requires thread-level verification",
        "CURSOR_CONFIG_VISIBILITY": "limited",
        "CODEX_AVAILABLE": "manual",
        "WEB_SEARCH_IN_THREAD": "available",
        "binaries": binaries,
        "command_probes": cmd_probes,
        "mcp": probe_mcp_config(),
        "cursor_artifacts": probe_cursor_rules(),
        "agent_layer_files": {
            "AGENTS.md": (ROOT / "AGENTS.md").is_file(),
            "agent_tools.yaml": (ROOT / "agent_tools.yaml").is_file(),
            "agent_layer.yaml": (ROOT / "agent_layer.yaml").is_file(),
        },
    }

    if args.ci:
        report["ci"] = evaluate_ci_status(binaries, cmd_probes)

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\n✓ 探针报告已写入 {REPORT_PATH.relative_to(ROOT)}")

    if args.ci:
        ci = report["ci"]
        if ci["blocked_env"]:
            print(f"  ⚠ BLOCKED_ENV（可选）: {', '.join(ci['blocked_env'])}")
        if ci["missing_required"]:
            print(f"  ✗ 缺失必需工具: {', '.join(ci['missing_required'])}")
            return 1
        if not ci["mcp_config_check_ok"]:
            print("  ✗ npm run check:mcp 未通过")
            return 1
        print(f"  ✓ CI 状态: {ci['status']}")
        return 0 if ci["status"] in ("passed", "partial") else 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
