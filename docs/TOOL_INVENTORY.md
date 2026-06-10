# 工具盘点（Tool Inventory）

Date: 2026-06-09（AL-03 更新）  
Agent: Cursor  
探针报告: `reports/tool_probe_report.json`  
机器清单: `agent_tools.yaml`

## 摘要

| 类别 | 状态 |
|------|------|
| Shell / Git | 可用 |
| Node / npm | 可用（v26 / 11.x） |
| Python / uv | 可用（3.14 / uv 0.11） |
| FFmpeg | 可用（8.0.1） |
| gh CLI | 可用（2.92） |
| Docker / Java / Maven | 不可用（本项目不依赖） |
| Web Search（本线程） | 可用 |
| MCP（配置） | 6 个 server 已写入 `.cursor/mcp.json` |
| MCP（当前线程可调用） | **unknown** — 需在对话工具列表中确认 |
| Codex | **manual** — 协议已兼容，本环境未验证 CLI |
| CURSOR_CONFIG_VISIBILITY | **limited** — 用户级 Settings 需人工确认 |

## A. 基础本地工具

| 工具 | Available | Probe | 备注 |
|------|-----------|-------|------|
| shell | yes | `pwd` | Cursor Shell 工具 |
| git | yes | `git status --short` | 分支 main，remote origin |
| node | yes | `node -v` | v26.0.0 |
| npm | yes | `npm -v` | 11.12.1 |
| pnpm | no | — | 未安装 |
| python3 | yes | `python3 --version` | 3.14.5 |
| uv | yes | `uv --version` | 0.11.19 |
| java | no | — | macOS 无 JRE |
| maven | no | — | — |
| docker | no | — | — |
| make | yes | `make --version` | GNU Make 3.81 |
| ffmpeg | yes | `ffmpeg -version` | 8.0.1 |
| pytest | yes | `python3 -m pytest` | 通过 gate |
| playwright CLI | conditional | `npx playwright --version` | 需 `apps/web/node_modules` |

## B. Cursor 相关

### 仓库内已存在

| 路径 | 说明 |
|------|------|
| `.cursor/mcp.json` | Workspace MCP：playwright, chrome-devtools, context7, filesystem, github, stitch |
| `.cursor/rules/` | 6 条规则 + 本轮新增 agent-layer / tool-usage / search-policy / safety-gates / user-view-testing |
| `.cursor/skills/browser-debug-check/SKILL.md` | 浏览器调试技能 |
| `docs/cursor_browser_ui_runbook.md` | UI 浏览器工作流 |
| `docs/cursor_tool_registry_check.md` | 线程工具注册表检查 |
| `AGENTS.md` | 跨 Agent 协议（已补强 Layer 2.0） |

### 需人工在 Cursor UI 确认

- Settings → MCP：各 server 是否 **Connected**
- 批准 MCP 后是否 **完全退出 Cursor 并重开对话**
- Multitask 是否关闭（浏览器任务）
- Skills / Hooks / Cloud Agent / Subagents 是否启用（依 Cursor 版本）
- Plan Mode / Design Mode 可用性

## C. Codex 相关

| 项 | 状态 |
|----|------|
| AGENTS.md | 已存在并兼容 Codex 读取链 |
| Codex CLI | `CODEX_AVAILABLE: manual` |
| Codex MCP | 见 `docs/CODEX_USAGE.md` |
| Handoff | `docs/CODEX_HANDOFF.md` 模板 |

## D. MCP 工具（配置 vs 可调用）

| name | configured | callable_now | safe_probe | recommended_use_cases | risks | fallback |
|------|------------|--------------|------------|----------------------|-------|----------|
| playwright | true | unknown | `npm run test` / MCP list | E2E、用户视角回归 | 线程未暴露工具 | Playwright CLI |
| chrome-devtools | true | unknown | MCP list | console/network/截图 | Multitask 无 MCP | Playwright |
| context7 | true | unknown | MCP list | React/Vite/FastAPI 文档 | — | WebSearch |
| filesystem | true | unknown | 读 README | 工作区内文件 | 越权路径 | Read/Grep |
| github | true | unknown | `gh auth status` | issue/PR 只读 | token 泄露 | gh CLI |
| stitch | true | unknown | `npm run check:stitch` | UI 设计原型 | 需 STITCH_API_KEY | DESIGN.md 手写 |

**禁止探针**：发布内容、删除远程数据、付费 API 调用、修改 `.env`。

## E. Web Search

- 本 Cursor Agent 线程：**available**（WebSearch 工具）
- 策略见 `docs/SEARCH_POLICY.md`
- 记录见 `docs/RESEARCH_NOTES.md`

## F. Browser / Playwright / 用户视角

| 能力 | 状态 |
|------|------|
| Playwright 依赖 | `@playwright/test` in apps/web |
| 本地服务 | `bash scripts/start_local.sh` |
| Review URL | `http://localhost:5173/?project_id=book_001&chapter_id=chapter_001` |
| API | `http://127.0.0.1:8000` |
| user_view_test | `python3 scripts/user_view_test.py` |
| Browser MCP | thread unknown |

## G. GitHub / 远程

| 项 | 状态 |
|----|------|
| remote | `origin` → github.com/alalapi-0/audiobook-cleaner-lab |
| gh CLI | 可用 |
| 本轮 push | **禁止**（默认协议） |
| 本轮 PR | **禁止**（默认协议） |

## H. Context7 / 官方文档

- MCP 已配置 `@upstash/context7-mcp`
- 本项目 recommended_docs 见 `agent_tools.yaml` 与 `docs/RESEARCH_NOTES.md`

## I. CI / pre-commit（AL-03）

| 入口 | 命令 | 说明 |
|------|------|------|
| 本地盘点 | `python3 scripts/tool_probe.py` | 只写报告，exit 0 |
| CI 门禁 | `python3 scripts/tool_probe.py --ci` | 必需工具缺失或 `check:mcp` 失败则 exit 1 |
| npm 别名 | `npm run agent:probe` / `npm run agent:probe:ci` | 根 `package.json` |
| GitHub Actions | `.github/workflows/tool-probe.yml` | push/PR 到 main；安装 ffmpeg + `npm ci` 后跑 `--ci` |
| pre-commit | `.pre-commit-config.yaml` | `pre-commit install` 后每次 commit 跑 `--ci` |

**CI 必需二进制**：`git`, `node`, `npm`, `python3`  
**CI 可选（缺失记 `BLOCKED_ENV`，不阻断）**：`uv`, `ffmpeg`, `gh`, `docker`, `make`, `java`  
**CI 额外检查**：`npm run check:mcp`（MCP 配置格式与安全，不调用 MCP 服务器）

报告字段 `ci.status`：`passed` | `partial`（仅有可选缺失）| `failed`

## 更新方式

每轮工具相关任务开始前运行：

```bash
python3 scripts/tool_probe.py
# 或 CI 等价：
npm run agent:probe:ci
```

将输出合并到本文件（重大变更时）并更新 `agent_tools.yaml`。
