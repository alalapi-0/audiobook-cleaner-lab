# MCP 使用技能 — audiobook-cleaner-lab

本文档说明本仓库为 Cursor Agent 配置的 MCP 工具、授权范围、降级策略与自动推进轮用法。

## 当前启用的 MCP

配置位于 [`.cursor/mcp.json`](../../.cursor/mcp.json)（合并模式，不覆盖已有同名 server）。

| MCP | 用途 | 是否需 Token |
|-----|------|--------------|
| **playwright** | 浏览器自动化：打开页面、点击、输入、截图、E2E 验收 | 否 |
| **chrome-devtools** | DevTools 级调试：console、network、performance、DOM | 否 |
| **context7** | 查询最新库/框架文档（prompt 中可写 `use context7`） | 否（可选 API Key 提升限额） |
| **filesystem** | 读写项目内文件、检查真实文件状态 | 否 |
| **github** | 读取仓库、提交、issue、PR、push 状态 | 是（`GITHUB_TOKEN` / `GITHUB_PERSONAL_ACCESS_TOKEN`） |

## Playwright MCP 用于什么

- 修改 Review 页、审核工作台等 **前端 UI** 后，必须用它（或 chrome-devtools）打开本地 dev server 验证。
- 检查核心用户路径：加载页面 → 交互 → 确认 DOM 与行为。
- 配合 console / network 检查，**不得**仅凭代码静态阅读判断 UI 成功。
- 本地默认地址：`http://localhost:5173`（Vite）；完整 API 流程需同时启动 FastAPI（见 [docs/agent-browser-verification.md](../agent-browser-verification.md)）。

## 文件系统 MCP 授权范围

- 仅授权 **当前项目根目录**（`${workspaceFolder}`），即本仓库 checkout 路径。
- **禁止**将 filesystem MCP 指向 `/`、`C:\`、`~` 或用户主目录根路径。
- 用于确认文件是否真实存在、内容是否已写入、目录结构是否符合预期。
- `data/` 下真实素材仍遵守 [AGENTS.md](../../AGENTS.md) 数据安全规则；MCP 不得绕过 `.gitignore` 策略向 Git 提交敏感内容。

## GitHub MCP 是否需要 Token

- **需要**：`@modelcontextprotocol/server-github` 读取私有仓库、创建 PR、查询 Actions 等操作依赖 Personal Access Token。
- 配置使用环境变量，**不在仓库中写死 token**：
  - 推荐在 shell 或 Cursor 环境中设置 `GITHUB_TOKEN`
  - MCP 映射为 `GITHUB_PERSONAL_ACCESS_TOKEN`（见 `.cursor/mcp.json` 的 `env` 块）
- 若本地未配置 token：GitHub MCP 可能无法连接；Agent 应 **降级** 为本地 `git` / `gh` CLI，并在报告中说明原因。

## 没有 API Key / Token 时如何降级

| 场景 | 降级方案 |
|------|----------|
| GitHub MCP 不可用 | 使用 `git status` / `git log` / `git diff`；若已安装 `gh` CLI 且已登录，用 `gh pr list` 等 |
| context7 不可用 | 阅读项目内 `docs/`、官方文档链接；标注「未使用 context7」 |
| Playwright MCP 不可用 | 运行 `npm run test`（apps/web Playwright smoke）；手动启动 dev server 并记录阻塞原因 |
| filesystem MCP 不可用 | 使用 Cursor 内置读文件工具；提交前仍须 `git diff` 确认 |

**原则**：缺少第三方 token 时进入 mock / dry-run，**不要卡死**整个自动推进流程，除非该 token 是当前任务唯一阻塞项。

## 后续自动推进轮如何使用这些 MCP

1. **轮次开始前**：确认 Cursor Settings → MCP 中相关 server 已加载（修改 `.cursor/mcp.json` 后需 **重启 Cursor** 或 Reload Window）。
2. **运行检查**：`python3 scripts/check_mcp_config.py` 或 `npm run check:mcp`。
3. **涉及 UI**：优先 Playwright MCP → 查看页面、console、network、核心流程 → 再跑 `npm run agent:check`。
4. **涉及文件**：用 filesystem MCP 或内置工具确认真实文件状态，不假设写入成功。
5. **涉及 GitHub**：先 `git diff` 检查是否泄露密钥，再决定是否 push / 开 PR。
6. **查文档**：prompt 中加 `use context7` 查询 React / Vite / FastAPI 等最新用法。
7. **完整门禁**：`python3 scripts/agent_gate.py`。

## 安全禁令

1. **禁止**将 token、cookie、API Key、session 写入仓库或 `.cursor/mcp.json`。
2. **禁止**授权 filesystem MCP 访问整个系统根目录或用户主目录。
3. **禁止**让 MCP 操作生产账号、真实用户数据或支付后台。
4. **禁止**在日志、验证报告或 commit message 中打印密钥。
5. 浏览器检查必须覆盖：**页面渲染**、**console**、**network**、**核心业务流程**——不允许只看截图或静态代码。

## 相关文件

- [`.cursor/mcp.json`](../../.cursor/mcp.json)
- [`.cursor/rules/mcp-agent-tools.mdc`](../../.cursor/rules/mcp-agent-tools.mdc)
- [`.cursor/rules/verification-gate.mdc`](../../.cursor/rules/verification-gate.mdc)
- [docs/agent-browser-verification.md](../agent-browser-verification.md)
- [scripts/check_mcp_config.py](../../scripts/check_mcp_config.py)
- [AGENTS.md](../../AGENTS.md) — MCP Tools 节

## 可选 MCP（未默认启用）

以下 server **未**写入 `.cursor/mcp.json`，确认包名与需求后可由维护者自行添加：

- **Brave Search / Tavily** 等搜索类 MCP — 需对应 API Key
- **Postgres / SQLite** MCP — 本项目当前以本地 JSON 为主，SQLite 接入后再评估

添加时请遵循合并原则，勿删除已有 server。
