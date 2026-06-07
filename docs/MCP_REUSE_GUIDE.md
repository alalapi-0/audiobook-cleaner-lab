# MCP 配置跨仓库复用指南

本文说明如何将本仓库的 MCP 治理方案迁移到新 Cursor 项目。

## 1. 建议复制的文件

| 文件/目录 | 说明 |
|-----------|------|
| `.cursor/mcp.json` | MCP server 定义（**复制后检查 filesystem 路径**） |
| `.cursor/rules/mcp-*.mdc` | Agent 行为规则（可选但推荐） |
| `scripts/check_mcp_config.js` | 配置检查脚本 |
| `scripts/print_mcp_manual_steps.js` | 人工步骤打印 |
| `scripts/stitch_mcp_proxy.mjs` | 若使用 stitch 本地 proxy |
| `docs/MCP_SETUP.md` | 启用指南 |
| `docs/MCP_TROUBLESHOOTING.md` | 故障排查 |
| `docs/MCP_AUDIT.md` | 审计模板（更新路径与日期） |
| `docs/MCP_REUSE_GUIDE.md` | 本文档 |
| `.env.example` | 环境变量模板 |

## 2. 不要直接复制的文件

| 文件 | 原因 |
|------|------|
| `.env` | 含真实密钥，且不应提交 |
| `.cursor/mcp.json.bak` | 本地备份，已在 `.gitignore` |
| 硬编码绝对路径的 mcp.json | 其他机器/路径会失效 |

## 3. 重新生成 filesystem 允许目录

**推荐（本仓库方案）：** 使用 `${workspaceFolder}`，无需改路径：

```json
"filesystem": {
  "command": "npx",
  "args": [
    "-y",
    "@modelcontextprotocol/server-filesystem",
    "${workspaceFolder}"
  ]
}
```

**备选：** 若目标环境不支持占位符，用脚本检测当前目录并写入绝对路径：

```bash
# 示例：生成当前仓库绝对路径（需人工合并进 mcp.json）
node -e "console.log(process.cwd())"
```

新仓库 checkout 后必须重新确认路径。

## 4. 检查 `.cursor/mcp.json`

```bash
npm run check:mcp
# 或
node scripts/check_mcp_config.js
```

确保 6 个 server key 存在：filesystem、playwright、chrome-devtools、context7、github、stitch。

## 5. package.json 合并

若目标仓库已有 `package.json`，仅合并 script：

```json
"check:mcp": "node scripts/check_mcp_config.js"
```

若已有 `check:mcp`，可添加 `check:mcp:config` 别名。

Stitch proxy 需 devDependencies：

```json
"@google/stitch-sdk": "^0.3.5",
"@modelcontextprotocol/sdk": "^1.25.2"
```

## 6. Cursor 里批准 MCP

复制配置后**仍需**在新机器上：

1. 打开 Cursor Settings → Tools & MCP
2. 逐 server 批准
3. 完全退出 Cursor
4. 重新打开新仓库
5. 新建普通前台 Agent 对话

## 7. GitHub 和 Stitch Token 处理

- 在目标机器设置 `GITHUB_TOKEN`、`STITCH_API_KEY`（或复制 `.env.example` → `.env` 后填入）
- **勿**将 token 写入 mcp.json 或提交到 Git
- 无 token 时 github / stitch 可能无法连接，但不阻塞其他 MCP

## 8. 为什么不要提交真实 `.env`

- `.env` 含 API Key，泄露风险高
- `.gitignore` 已排除 `.env` 与 `.env.*`（保留 `.env.example`）
- CI 与 Cursor 应通过各自 secret 机制注入

## 9. 为什么新仓库需要重新打开 Cursor

- MCP stdio 进程在 Cursor 启动时注册
- 新仓库的 `.cursor/mcp.json` 只在打开该 workspace 时加载
- 批准后需重启以 spawn 新子进程

## 10. 如何判断当前线程真的暴露了 MCP 工具

| 方法 | 说明 |
|------|------|
| 新对话中列出工具 | Agent 应能看到 playwright / filesystem 等专用工具 |
| 实际调用 | 如 browser_navigate、MCP filesystem 读写 |
| `npm run check:mcp` | **仅**验证配置文件，**不能**证明当前线程可用 |
| Settings → MCP | 显示 connected 也不等于旧对话已注入工具 |

若工具仍不可用：见 [MCP_TROUBLESHOOTING.md](MCP_TROUBLESHOOTING.md)。

## 11. 本仓库特有项

- Stitch 设计归档：`docs/design/stitch/`
- 浏览器验收 runbook：`docs/cursor_browser_ui_runbook.md`
- Agent 规范：`AGENTS.md`

迁移 UI 项目时可一并复制 `docs/design/` 与 `.cursor/rules/cursor-browser-ui.mdc`。
