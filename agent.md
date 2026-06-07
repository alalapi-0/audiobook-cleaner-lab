# agent.md — Agent 快速入口

> 与 [AGENTS.md](AGENTS.md) 互补：本文档供 Cursor / Codex 快速定位工具与文档。

## 必读

1. [README.md](README.md)
2. [AGENTS.md](AGENTS.md)
3. [PROJECT_STATE.md](PROJECT_STATE.md)
4. [docs/agent_workflow/README.md](docs/agent_workflow/README.md)

## MCP（6 个）

| MCP | 用途 |
|-----|------|
| chrome-devtools | 浏览器调试 |
| context7 | 库文档 |
| filesystem | 项目文件 |
| github | Git / PR |
| playwright | E2E |
| **stitch** | **UI 设计** |

检查：`npm run check:mcp` · `npm run check:stitch` · `npm run check:cursor-mcp`

## Stitch Design MCP

**何时用**：新页面、审核台改版、Dashboard、Debug 面板。

**先读**：

- [docs/design/DESIGN.md](docs/design/DESIGN.md)
- [docs/design/stitch/README.md](docs/design/stitch/README.md)
- [docs/design/stitch/UI_TASKS.md](docs/design/stitch/UI_TASKS.md)
- [docs/design/stitch/PROMPT_TEMPLATES.md](docs/design/stitch/PROMPT_TEMPLATES.md)

**流程**：Stitch 生成 → 存入 `exports/` / `screenshots/` → 拆任务 → `apps/web/` 实现 → Playwright/CDP 验证。

**禁止**：无审查覆盖业务代码；提交 API Key。

**Key**：环境变量 `STITCH_API_KEY`（见 `.env.example`）。

## 测试

| 类型 | 文档 |
|------|------|
| 浏览器 | [docs/testing/BROWSER_TESTING.md](docs/testing/BROWSER_TESTING.md) |
| 真实 API | [docs/testing/REAL_API_TESTING.md](docs/testing/REAL_API_TESTING.md) |
| 用户视角 | [docs/testing/USER_PERSPECTIVE_TESTING.md](docs/testing/USER_PERSPECTIVE_TESTING.md) |

## Cursor Browser UI Workflow

1. **普通前台 Agent only**；禁止 Multitask 控制浏览器。
2. 任务前确认**当前线程**是否暴露 stitch / chrome-devtools / playwright 工具。
3. 每轮 UI：**before 截图 + console/network → 改一个切片 → after 检查 → 测试**。
4. 缺工具 → `BLOCKED: MISSING_FROM_THREAD_TOOL_REGISTRY`，完全退出 Cursor 后新建对话。
5. 本仓库本地 Web：**不用** wechat-chrome-session。

详见 [docs/cursor_browser_ui_runbook.md](docs/cursor_browser_ui_runbook.md) · Prompt：[docs/prompts/CURSOR_UI_IMPLEMENTATION_PROMPT.md](docs/prompts/CURSOR_UI_IMPLEMENTATION_PROMPT.md)

## 验收

```bash
python3 scripts/check_repo.py
npm run check:mcp
npm run check:stitch
npm run check:cursor-mcp
python3 scripts/agent_gate.py
```
