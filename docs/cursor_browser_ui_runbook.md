# Cursor 浏览器 UI 推进 Runbook

本文档面向在本仓库中使用 **Cursor Agent** 进行浏览器检查、Stitch 设计、UI 实现与回归验证的场景。目标不是替代业务开发，而是让 Agent **稳定地**使用 MCP 工具完成真实页面闭环。

> 相关文档：[cursor_tool_registry_check.md](cursor_tool_registry_check.md) · [AGENTS.md](../AGENTS.md) · [prompts/CURSOR_UI_IMPLEMENTATION_PROMPT.md](prompts/CURSOR_UI_IMPLEMENTATION_PROMPT.md)

---

## 1. Cursor 浏览器任务的基本原则

### MCP ready ≠ 当前 Agent 线程可用

- **Settings → Tools & MCP** 中显示 server 为 ready，只说明 Cursor 进程已加载该 MCP server。
- **当前 Agent 对话线程** 可能仍使用批准 MCP **之前**的旧工具注册表，因此对话里调用工具会报 `server does not exist` 或工具列表为空。
- 终端 `cursor-agent mcp list` 显示 ready，同样**不能**证明当前对话线程已暴露对应原生工具。

### Settings 中启用 ≠ 旧对话能调用

- 在设置里新启用或批准 MCP 后，**已打开的旧 Agent 对话不会自动刷新工具注册表**。
- 必须在批准后 **完全退出 Cursor**（不是仅 Reload Window），重新打开本仓库，并 **新建普通前台 Agent 对话**。

### 批准 MCP 后的标准动作

1. 在 Cursor Settings → Tools & MCP 中批准所需 server。
2. **完全退出 Cursor**（macOS：Cmd+Q；确保进程结束）。
3. 重新打开本仓库。
4. **新建**普通前台 Agent 对话（不要复用旧线程）。
5. **禁用 Multitask**（见下文）。
6. 执行任务前再次确认当前线程实际暴露的工具。

### 必须使用普通前台 Agent

- 所有涉及浏览器控制、页面截图、console/network 检查、Playwright E2E 的任务，必须使用 **普通前台 Agent**。
- **禁止** Multitask 模式或后台子 Agent 执行浏览器控制任务（子 Agent 可能未继承 Workspace MCP）。

### 任务开始前必须检查当前线程工具

Agent 在开始浏览器任务前，必须确认当前对话是否实际暴露了目标 MCP 工具（例如 `browser_snapshot`、`take_screenshot`、`list_console_messages` 等），而不是仅检查配置文件或 CLI。

### 缺工具时必须 BLOCKED，禁止假装执行

若当前线程没有暴露目标工具，**立即停止**，输出：

```
BLOCKED: MISSING_FROM_THREAD_TOOL_REGISTRY
```

并说明用户应：

1. 完全退出 Cursor；
2. 重新打开仓库；
3. 在 Settings → Tools & MCP 中确认工具 ready；
4. 新建普通前台 Agent 对话；
5. 禁用 Multitask；
6. 重新执行任务。

**不得**在无浏览器工具的情况下声称「已截图」「已检查 console」「页面正常」。

---

## 2. 工具选择规则

### 普通本地 Web 项目 UI 优化（本仓库默认场景）

本仓库为 **本地 React + Vite Review 审核台**，属于普通本地 Web 项目。优先使用：

| MCP | 用途 |
|-----|------|
| **stitch** | 生成 UI 设计依据、原型、截图、HTML 导出 |
| **chrome-devtools** | 检查页面、console、network、截图、DOM |
| **playwright** | E2E 回归、稳定自动化验收 |
| **filesystem** | 检查代码与产物、确认真实文件状态 |
| **context7** | 查询 React / Vite / wavesurfer 等前端库文档 |
| **github** | commit / push / issue / PR |

**本仓库不使用** `wechat-chrome-session`（非微信公众号项目）。

### 微信公众号已登录页面操作（其他项目适用，本仓库不适用）

若在其他仓库处理 **微信公众号已登录页面**，**只使用**：

- `wechat-chrome-session`

**禁止使用**：

- 普通 `chrome-devtools`（会新开未登录浏览器上下文）；
- `playwright`（隔离浏览器，无登录态）；
- `browser_tabs` / `new_page` / `navigate_page` 等会新开未登录浏览器的工具。

### 真实页面 UI 优化必须执行的检查

每一轮 UI 改造必须完成以下观察记录：

| 阶段 | 动作 |
|------|------|
| Before | 打开页面 → 截图 → 检查 console → 检查 network → 记录 before 状态 |
| 实现 | 修改 UI 代码（单一切片） |
| After | 再打开页面 → 截图 → 检查 console → 检查 network → 记录 after 状态 |
| 修复 | 修复发现的问题，必要时重复 after 检查 |

不得仅凭代码 diff 或 Stitch 导出物宣布 UI 完成。

---

## 3. 标准 UI 优化流程

固定流程（每轮只改 **一个主要 UI 切片**）：

1. **读取上下文**：README、AGENTS、ROADMAP、`docs/design/`、`docs/design/stitch/UI_TASKS.md`
2. **启动项目**：`bash scripts/start_local.sh` 或 `npm run dev`（确保 API + Web 可访问）
3. **打开页面**：使用 chrome-devtools 或 playwright 打开 Review 页（如 `http://127.0.0.1:5173/?project_id=book_001&chapter_id=chapter_001`）
4. **保存 before screenshot**：存入 `docs/design/stitch/screenshots/` 或轮次报告目录
5. **读取 Stitch 设计**：查阅已有导出物，或调用 Stitch MCP 生成/更新设计参考
6. **选择一个 UI 改造切片**：例如「波形区布局」「切点列表样式」——每轮只做一个
7. **修改代码**：在 `apps/web/` 落地，不改变业务逻辑
8. **重新打开页面**：热更新后刷新或重新导航
9. **检查 console / network**：无 error、无异常 4xx/5xx
10. **检查响应式**：必要时调整视口宽度
11. **运行测试**：`npm run test`、`npm run build` 或 round 文档声明的验收命令
12. **保存 after screenshot**：与 before 对比
13. **更新文档**：必要时更新 `docs/design/` 或 round 文件
14. **commit / push**：用户明确要求时执行；提交前 `git diff` 确认无密钥

---

## 4. 当前线程工具检查

### 规则

若用户要求使用某个 MCP（如 chrome-devtools、playwright、stitch），Agent **必须先确认「当前对话线程」是否暴露对应原生工具**。

**不要只依赖**：

- `cursor-agent mcp list`（CLI 层 ready）；
- Settings 中的 ready 状态；
- `.cursor/mcp.json` 文件存在。

### 如何自检（Agent 侧）

1. 查看当前对话可用工具列表中是否包含目标 server 的原生工具名。
2. 若不确定，可运行 `bash scripts/check_cursor_mcp_status.sh` 辅助了解 CLI 层状态，但**脚本结果不能替代线程检查**。
3. 若调用工具失败且报 server 不存在，视为线程未继承注册表。

### BLOCKED 输出模板

```
BLOCKED: MISSING_FROM_THREAD_TOOL_REGISTRY

缺失工具：<server 名称，如 chrome-devtools / playwright / stitch>

请执行：
1. 完全退出 Cursor（Cmd+Q）
2. 重新打开本仓库
3. Settings → Tools & MCP → 确认上述 server 为 ready
4. 新建普通前台 Agent 对话
5. 禁用 Multitask
6. 使用 docs/prompts/CURSOR_UI_IMPLEMENTATION_PROMPT.md 重新发起任务
```

### MCP 配置检查（仓库侧）

```bash
npm run check:cursor-mcp    # CLI 层 MCP 状态
npm run check:mcp           # 配置格式与安全
npm run check:stitch        # Stitch 专项
```

---

## 5. 本仓库工具隔离摘要

| 场景 | 使用 | 禁止 |
|------|------|------|
| 本地 Review 审核台 UI | stitch + chrome-devtools + playwright | wechat-chrome-session |
| 微信公众号已登录页（其他项目） | wechat-chrome-session only | chrome-devtools、playwright、browser_tabs |

---

## 6. 参考链接

- [cursor_tool_registry_check.md](cursor_tool_registry_check.md) — 线程工具注册排查表
- [agent-browser-verification.md](agent-browser-verification.md) — 浏览器验证闭环
- [testing/BROWSER_TESTING.md](testing/BROWSER_TESTING.md) — 浏览器测试说明
- [.cursor/rules/cursor-browser-ui.mdc](../.cursor/rules/cursor-browser-ui.mdc)
- [.cursor/rules/no-multitask-for-browser.mdc](../.cursor/rules/no-multitask-for-browser.mdc)
