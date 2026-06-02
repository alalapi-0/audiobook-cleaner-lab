#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""轻量 MCP 配置检查 — 验证 .cursor/mcp.json 格式、playwright 与危险路径。"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MCP_PATH = ROOT / ".cursor" / "mcp.json"

REQUIRED_SERVERS = (
    "chrome-devtools",
    "context7",
    "filesystem",
    "github",
    "playwright",
)

# filesystem args 中视为危险的根路径（大小写不敏感匹配片段）
DANGEROUS_PATH_FRAGMENTS = (
    "/",
    "c:\\",
    "c:/",
    "~",
    "$home",
    "%userprofile%",
    "/users/",
    "/home/",
)

# 允许的安全占位符
SAFE_WORKSPACE_PLACEHOLDERS = ("${workspaceFolder}", "${workspaceRoot}")


def load_mcp_config() -> tuple[dict | None, list[str]]:
    """加载并解析 .cursor/mcp.json。"""
    issues: list[str] = []
    if not MCP_PATH.is_file():
        return None, [f"缺失: {MCP_PATH.relative_to(ROOT)}"]

    try:
        data = json.loads(MCP_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, [f"JSON 无法解析: {exc}"]

    if not isinstance(data, dict):
        return None, ["根对象必须是 JSON object"]

    servers = data.get("mcpServers")
    if not isinstance(servers, dict):
        issues.append("缺少或无效的 mcpServers 对象")

    return data, issues


def check_required_servers(servers: dict) -> list[str]:
    """确认包含全部必需 MCP server。"""
    return [f"缺少 MCP server: {name}" for name in REQUIRED_SERVERS if name not in servers]


def check_filesystem_scope(servers: dict) -> list[str]:
    """检查 filesystem MCP 是否指向危险路径。"""
    issues: list[str] = []
    fs = servers.get("filesystem")
    if not isinstance(fs, dict):
        return issues

    args = fs.get("args") or []
    if not isinstance(args, list):
        return ["filesystem.args 必须是数组"]

    path_args = [str(a) for a in args if isinstance(a, (str, int, float))]
    # 通常最后一个 arg 是目录路径
    for raw in path_args:
        norm = raw.strip().lower().replace("\\", "/")
        if any(ph in raw for ph in SAFE_WORKSPACE_PLACEHOLDERS):
            continue
        if norm in ("/", "c:/", "c:\\"):
            issues.append(f"filesystem 授权范围过宽: {raw!r}")
            continue
        if norm.startswith("~/") or norm == "~":
            issues.append(f"filesystem 指向用户主目录: {raw!r}")
            continue
        for frag in DANGEROUS_PATH_FRAGMENTS:
            if frag == "/":
                continue
            if frag in norm and norm.endswith(frag.rstrip("/")):
                issues.append(f"filesystem 可能授权过宽: {raw!r}")

    if not path_args:
        issues.append("filesystem 未指定授权目录")

    return issues


def summarize_servers(servers: dict) -> None:
    """输出 MCP 配置摘要（不打印 token）。"""
    print("\nMCP 配置摘要:")
    for name, cfg in sorted(servers.items()):
        if not isinstance(cfg, dict):
            print(f"  - {name}: (无效配置)")
            continue
        cmd = cfg.get("command", "?")
        args = cfg.get("args") or []
        arg_preview = " ".join(str(a) for a in args[:4])
        if len(args) > 4:
            arg_preview += " ..."
        has_env = "env" in cfg and isinstance(cfg["env"], dict)
        env_keys = list(cfg["env"].keys()) if has_env else []
        env_note = f", env keys: {env_keys}" if env_keys else ""
        print(f"  - {name}: {cmd} {arg_preview}{env_note}")


def main() -> int:
    """执行 MCP 配置检查。"""
    print("=" * 50)
    print("MCP 配置检查 — audiobook-cleaner-lab")
    print("=" * 50)

    data, issues = load_mcp_config()
    if data is None:
        for issue in issues:
            print(f"  ✗ {issue}")
        return 1

    servers = data.get("mcpServers") or {}
    if not isinstance(servers, dict):
        print("  ✗ mcpServers 无效")
        return 1

    issues.extend(check_required_servers(servers))
    issues.extend(check_filesystem_scope(servers))

    summarize_servers(servers)

    optional = []
    for name in REQUIRED_SERVERS:
        if name not in servers:
            optional.append(name)
    if optional:
        print(f"\n提示: 未配置的 server: {', '.join(optional)}")

    if issues:
        print("\n检查未通过:")
        for issue in issues:
            print(f"  ✗ {issue}")
        return 1

    print("\n✓ MCP 配置检查通过")
    print("  修改 .cursor/mcp.json 后请重启 Cursor 或 Reload Window")
    return 0


if __name__ == "__main__":
    sys.exit(main())
