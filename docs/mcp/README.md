# MCP 文档总览

本目录说明 **audiobook-cleaner-lab** 在 Cursor 中使用的 Workspace MCP Servers。

## 文档索引

| 文档 | 内容 |
|------|------|
| [WORKSPACE_MCP_SERVERS.md](WORKSPACE_MCP_SERVERS.md) | 各 MCP 用途与配置 |
| [../agent_skills/mcp_usage_skill.md](../agent_skills/mcp_usage_skill.md) | 降级策略与自动推进用法 |
| [../design/stitch/STITCH_MCP_SETUP.md](../design/stitch/STITCH_MCP_SETUP.md) | Stitch 专项配置 |

## 配置文件

- [`.cursor/mcp.json`](../../.cursor/mcp.json) — Workspace MCP 配置（合并模式）
- 修改后需 **重启 Cursor 或 Reload Window**

## 检查命令

```bash
npm run check:mcp      # 全量 MCP 格式与安全
npm run check:stitch   # Stitch 专项检查
python3 scripts/check_mcp_config.py
```

## 安全原则

- Token / API Key **仅**通过环境变量提供
- 提交前 `git diff` 确认无密钥泄露
- filesystem 仅授权 `${workspaceFolder}`
