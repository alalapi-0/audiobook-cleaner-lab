# Workspace MCP Servers

配置源：[`.cursor/mcp.json`](../../.cursor/mcp.json)

| MCP | 传输 | 用途 |
|-----|------|------|
| **chrome-devtools** | stdio (npx) | 浏览器调试：console、network、DOM、performance |
| **context7** | stdio (npx) | 查询 React / Vite / FastAPI 等第三方库文档 |
| **filesystem** | stdio (npx) | 读写当前项目目录（`${workspaceFolder}`） |
| **github** | stdio (npx) | 仓库、issue、PR、分支、提交（需 `GITHUB_TOKEN`） |
| **playwright** | stdio (npx) | 浏览器自动化、E2E、页面交互验收 |
| **stitch** | stdio (node proxy) | UI 设计、原型、截图、HTML 导出（需 `STITCH_API_KEY`） |

## 各 MCP 详细说明

### chrome-devtools

- 修改 Review 页、审核台后做 DevTools 级检查
- 必须覆盖：页面渲染、console、network、核心流程
- 与 Playwright 二选一或组合使用

### context7

- prompt 中可加 `use context7` 查询最新文档
- 无 API Key 时仍可用（可能有速率限制）

### filesystem

- **仅**授权本仓库根目录
- 禁止指向 `/`、`~`、`C:\` 或用户主目录
- 遵守 `data/` 与 `.gitignore` 规则

### github

- 环境变量：`GITHUB_TOKEN` → MCP 内 `GITHUB_PERSONAL_ACCESS_TOKEN`
- 不可用時降级为 `git` / `gh` CLI

### playwright

- 本地默认：`http://localhost:5173`（Vite）
- 完整 API 流程需同时启动 FastAPI（见 [agent-browser-verification.md](../agent-browser-verification.md)）

### stitch

- 本地 proxy：`scripts/stitch_mcp_proxy.mjs`
- 环境变量：`STITCH_API_KEY`
- 设计结果归档：`docs/design/stitch/`
- 详见 [STITCH_MCP_SETUP.md](../design/stitch/STITCH_MCP_SETUP.md)

## 启用检查

1. Cursor Settings → MCP → 确认上述 server 已加载
2. `npm run check:mcp && npm run check:stitch`
3. 涉及 UI 任务时优先读 [docs/design/DESIGN.md](../design/DESIGN.md)

## 不可用时

在 round 报告中记录原因，按 [mcp_usage_skill.md](../agent_skills/mcp_usage_skill.md) 降级，勿反复无意义重装。
