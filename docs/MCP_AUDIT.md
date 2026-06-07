# MCP 配置审计报告

> 审计时间：2026-06-07  
> 仓库路径：`/Users/alalapi/PycharmProjects/audiobook-cleaner-lab`  
> 本轮类型：仓库级 MCP 配置治理（非功能开发）

## 1. 仓库现状摘要

| 检查项 | 状态 |
|--------|------|
| `.cursor/` 目录 | ✅ 存在 |
| `.cursor/mcp.json` | ✅ 存在，已配置 6 个 server |
| `.env` | ❌ 不存在（正常，不应提交） |
| `.env.example` | ✅ 存在，本轮补全 GitHub 变量 |
| `docs/` | ✅ 存在 |
| `scripts/` | ✅ 存在 |
| `scripts/check_mcp_config.js` | ✅ 存在，本轮增强 |
| `scripts/check_mcp_config.py` | ✅ 存在（Python 等价检查） |
| `scripts/stitch_mcp_proxy.mjs` | ✅ 存在 |
| `package.json` | ✅ 存在，已有 `check:mcp` |
| `AGENTS.md` / `README.md` / `PROJECT_STATE.md` | ✅ 存在 |
| 项目内 MCP 文档 | ✅ `docs/mcp/`、`docs/agent_skills/mcp_usage_skill.md` 等 |
| 疑似硬编码密钥 | ✅ 未发现（mcp.json 使用 `${env:...}` 占位符） |

## 2. 已有 MCP Server 配置

| Server key | 传输 | 启动方式 | 需要 Token |
|------------|------|----------|------------|
| `filesystem` | stdio | `npx @modelcontextprotocol/server-filesystem ${workspaceFolder}` | 否 |
| `playwright` | stdio | `npx @playwright/mcp@latest --isolated` | 否 |
| `chrome-devtools` | stdio | `npx chrome-devtools-mcp@latest` | 否 |
| `context7` | stdio | `npx @upstash/context7-mcp@latest` | 否 |
| `github` | stdio | `npx @modelcontextprotocol/server-github` | 是（`GITHUB_TOKEN` → `GITHUB_PERSONAL_ACCESS_TOKEN`） |
| `stitch` | stdio | `node scripts/stitch_mcp_proxy.mjs` | 是（`STITCH_API_KEY`） |

**缺少的 server：** 无。6 个目标 server 均已配置。

## 3. 配置层级说明

| 层级 | 内容 | 谁负责 |
|------|------|--------|
| 仓库可配置 | `.cursor/mcp.json`、检查脚本、文档、`.env.example` | Agent / 维护者 |
| Cursor UI 批准 | Settings → Tools & MCP 中逐 server 批准 | **用户手动** |
| 完全重启生效 | 修改 mcp.json 或批准后需完全退出 Cursor 再重开 | **用户手动** |
| 新对话暴露工具 | 新建**普通前台 Agent** 对话后工具才注入当前线程 | **用户手动** |
| Token / API Key | `GITHUB_TOKEN`、`STITCH_API_KEY` 等 | **用户自行提供** |

## 4. filesystem 路径策略

当前使用 `${workspaceFolder}` 占位符（优于硬编码绝对路径）：

- Cursor 打开仓库时自动解析为当前 checkout 根目录
- 新仓库复用时**无需**改路径
- 检查脚本同时接受 `${workspaceFolder}` / `${workspaceRoot}` 为安全值

## 5. stitch 状态

**已配置**，非待补充：

- 启动命令：`node scripts/stitch_mcp_proxy.mjs`
- 依赖：`@google/stitch-sdk`、`@modelcontextprotocol/sdk`（根 `package.json` devDependencies）
- 详见 [docs/design/stitch/STITCH_MCP_SETUP.md](design/stitch/STITCH_MCP_SETUP.md)

## 6. 本轮计划修改的文件

| 文件 | 操作 |
|------|------|
| `docs/MCP_AUDIT.md` | 创建（本文档） |
| `docs/MCP_SETUP.md` | 创建 |
| `docs/MCP_TROUBLESHOOTING.md` | 创建 |
| `docs/MCP_REUSE_GUIDE.md` | 创建 |
| `.env.example` | 更新（补 GitHub 变量，规范占位符） |
| `scripts/check_mcp_config.js` | 增强（文档与 .env.example 检查） |
| `scripts/print_mcp_manual_steps.js` | 创建 |
| `.gitignore` | 追加 `.cursor/mcp.json.bak` |
| `.cursor/mcp.json.bak` | 创建备份（不入 Git） |
| `.cursor/mcp.json` | **不修改**（已有配置完整且安全） |

## 7. 本轮不修改的内容

- 业务代码（`apps/`、`packages/` 等）
- `.cursor/mcp.json` 主体（6 server 已齐全，沿用 `${workspaceFolder}` 与 stitch proxy）
- `package.json` 的 name / version / dependencies（已有 `check:mcp`）
- 真实 `.env` 文件（不存在，不创建）
- 任何 GitHub 写操作或 Stitch API 调用

## 8. 已知线程级问题（背景）

以下现象属于 **Cursor 运行时加载** 问题，不能仅靠仓库文件修复：

- CLI 显示 server 存在但 not loaded / needs approval
- 当前 Agent 线程未暴露 MCP 专用工具
- `ListMcpResources` 返回空

恢复步骤见 [MCP_SETUP.md](MCP_SETUP.md) 与 [MCP_TROUBLESHOOTING.md](MCP_TROUBLESHOOTING.md)。

## 9. 验收命令

```bash
node scripts/check_mcp_config.js
npm run check:mcp
node scripts/print_mcp_manual_steps.js
```
