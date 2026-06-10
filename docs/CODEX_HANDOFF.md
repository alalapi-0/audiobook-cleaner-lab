# Codex Handoff

> 模板：Cursor 将当前状态交给 Codex 时填写。复制本文件内容到新对话或 Codex 任务描述。

## Repo

`audiobook-cleaner-lab` — 个人有声书音频清洗与文本对齐剪辑（Python FastAPI + React Vite Review UI）

## Current branch

`main`（填写实际分支）

## Current goal

（本轮要给 Codex 做的**一件事**）

## Must read

- AGENTS.md
- agent_layer.yaml
- agent_tools.yaml
- docs/TOOL_USAGE_POLICY.md
- docs/AGENT_RUNBOOK.md
- reports/latest-agent-report.json
- docs/CODEX_HANDOFF.md（本文件）

## Current P0/P1

| ID | 描述 | 状态 |
|----|------|------|
| | | |

## Latest gate result

- 文件: `reports/gate_result.json`
- status: （passed/failed）
- failed: （列表）

## Relevant files

- （路径列表）

## Do not touch

- `.env`
- `data/` 用户真实素材
- 原始 wav 覆盖逻辑
- `.cursor/mcp.json`（除非任务明确要求）

## Tools expected

- shell, git, python3, npm
- （可选 MCP：playwright, context7, github）

## Commands to run

```bash
python3 scripts/tool_probe.py
python3 scripts/agent_gate.py
# 专项命令：
```

## Acceptance criteria

- [ ] gate 通过或 BLOCKED 已记录
- [ ] 无真实 API / 无 push
- [ ] `reports/latest-agent-report.json` 已更新
- [ ] tool_usage 已记录

## Return format

Codex 结束时返回：

1. 变更文件列表
2. 命令与结果
3. P0/P1 状态
4. 建议下一轮（Cursor 或 Codex）
