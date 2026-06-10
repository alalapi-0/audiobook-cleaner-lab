# Codex 使用指南

即使当前 Codex 额度不足，本仓库协议已兼容 Codex CLI / Cloud。

## Codex 适合的任务

- 大范围重构（packages/ 跨模块）
- 长程推进（多文件特性）
- 代码审查 / PR review
- 测试生成（大批量）
- worktree 并行任务
- 难问题攻关（对齐算法、性能）

## Cursor 适合的任务

- 本地快速修复
- UI 调试与 Browser MCP
- MCP 工具联动
- 小轮次实现
- Agent Layer / 文档 / 规则落地

## Codex 启动前必读

1. [AGENTS.md](../AGENTS.md)
2. [agent_layer.yaml](../agent_layer.yaml)
3. [agent_tools.yaml](../agent_tools.yaml)
4. [docs/TOOL_USAGE_POLICY.md](TOOL_USAGE_POLICY.md)
5. [docs/AGENT_RUNBOOK.md](AGENT_RUNBOOK.md)
6. [reports/latest-agent-report.json](../reports/latest-agent-report.json)
7. [docs/CODEX_HANDOFF.md](CODEX_HANDOFF.md)（若由 Cursor 交接）

## 任务建议格式

- plan first
- small scope（单轮）
- no real API
- no real publish
- run gate（或记录 BLOCKED_ENV）
- generate report

## 额度有限时的策略

- 仅高价值任务
- 不用 Codex 润色普通文档
- 不用 Codex 做小修小补
- 用 Cursor 生成 [CODEX_HANDOFF.md](CODEX_HANDOFF.md) 压缩上下文

## Codex 配置参考（官方）

- AGENTS.md: https://developers.openai.com/codex/guides/agents-md
- MCP: https://developers.openai.com/codex/concepts/customization
- CLI: https://developers.openai.com/codex/cli

MCP 可镜像 `.cursor/mcp.json` 能力（在项目或 `~/.codex/config.toml` 配置）。
