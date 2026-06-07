# MCP 配置与启用指南

本仓库为 Cursor Agent 配置了 6 个 Workspace MCP Server。配置文件位于：

```text
.cursor/mcp.json
```

## 各 MCP 用途与 Token 需求

| MCP | 用途 | 需要 Token |
|-----|------|------------|
| **filesystem** | 读写当前仓库内文件，确认真实文件状态 | 否 |
| **playwright** | 浏览器自动化、E2E、页面交互与截图验收 | 否 |
| **chrome-devtools** | DevTools 级调试：console、network、DOM、性能 | 否 |
| **context7** | 查询第三方库/框架官方文档 | 否 |
| **github** | 仓库、issue、PR、分支、提交等 GitHub 操作 | **是** |
| **stitch** | UI 设计、原型、截图、HTML 导出 | **是** |

### Token 环境变量

| 变量 | 用于 | 说明 |
|------|------|------|
| `GITHUB_TOKEN` 或 `GITHUB_PERSONAL_ACCESS_TOKEN` | github MCP | mcp.json 将 `GITHUB_TOKEN` 映射为 `GITHUB_PERSONAL_ACCESS_TOKEN` |
| `STITCH_API_KEY` | stitch MCP | 本地 proxy `scripts/stitch_mcp_proxy.mjs` 读取 |

示例模板见根目录 [`.env.example`](../.env.example)。**勿将真实密钥提交到 Git。**

## 当前 mcp.json 配置摘要

```json
{
  "mcpServers": {
    "filesystem":   "npx @modelcontextprotocol/server-filesystem ${workspaceFolder}",
    "playwright":   "npx @playwright/mcp@latest --isolated",
    "chrome-devtools": "npx chrome-devtools-mcp@latest",
    "context7":     "npx @upstash/context7-mcp@latest",
    "github":       "npx @modelcontextprotocol/server-github (+ GITHUB_TOKEN env)",
    "stitch":       "node scripts/stitch_mcp_proxy.mjs (+ STITCH_API_KEY env)"
  }
}
```

filesystem 使用 `${workspaceFolder}` 而非硬编码绝对路径，便于仓库迁移。

Stitch 详情：[docs/design/stitch/STITCH_MCP_SETUP.md](design/stitch/STITCH_MCP_SETUP.md)

## 在新仓库中复用

见 [MCP_REUSE_GUIDE.md](MCP_REUSE_GUIDE.md)。

## 检查配置是否正确

```bash
npm install          # stitch proxy 依赖
npm run check:mcp    # 或 node scripts/check_mcp_config.js
npm run check:stitch # stitch 专项（可选）
node scripts/print_mcp_manual_steps.js  # 打印人工启用步骤
```

## 人工启用步骤（必须）

仓库文件写入 `.cursor/mcp.json` **不会**让当前 Agent 对话自动获得 MCP 工具。请按顺序完成：

```text
1. 打开 Cursor Settings
2. 进入 Tools & MCP
3. 找到当前仓库配置的 MCP server
4. 对 filesystem / playwright / chrome-devtools / context7 / github / stitch 逐一批准
5. 如果 github 或 stitch 需要密钥，先配置对应环境变量或在 Cursor 支持的位置填写
6. 完全退出 Cursor，不只是关闭窗口
7. 重新打开当前仓库
8. 新建普通前台 Agent 对话
9. 不要使用 Multitask 模式测试 MCP
10. 在新对话中让 Agent 检查当前线程暴露的工具列表
```

### 为什么需要批准？

Cursor 将 MCP server 视为需用户显式授权的外部进程。未批准时 server 可能显示 **not loaded** 或 **needs approval**。

### 为什么批准后还要重启 Cursor？

MCP 进程在 Cursor 启动时注册。修改 `mcp.json` 或首次批准后，仅 Reload Window 有时不够；**完全退出并重启**可确保 stdio 子进程与工具注册表刷新。

### 为什么要新建普通前台 Agent 对话？

- 工具列表在**对话创建时**绑定到 Agent 线程
- 已存在的对话（含 Multitask 子 Agent）不会 retroactively 获得新 MCP 工具
- Multitask / 后台子 Agent 可能**未继承** Workspace MCP（见 `.cursor/rules/no-multitask-for-browser.mdc`）

### 如何确认当前线程已暴露工具？

在新对话中让 Agent 列出可用 MCP 工具，或观察是否能调用例如 `browser_navigate`（playwright）、filesystem 读写、context7 文档查询等。**不要**仅凭 `npm run check:mcp` 通过就认为当前线程可用。

## 相关文档

- [MCP_AUDIT.md](MCP_AUDIT.md) — 审计记录
- [MCP_TROUBLESHOOTING.md](MCP_TROUBLESHOOTING.md) — 故障排查
- [MCP_REUSE_GUIDE.md](MCP_REUSE_GUIDE.md) — 跨仓库复用
- [docs/mcp/WORKSPACE_MCP_SERVERS.md](mcp/WORKSPACE_MCP_SERVERS.md) — 各 server 详细说明
- [docs/agent_skills/mcp_usage_skill.md](agent_skills/mcp_usage_skill.md) — Agent 使用与降级策略
