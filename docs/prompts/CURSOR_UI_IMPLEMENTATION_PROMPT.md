# Cursor UI 实现启动 Prompt 模板

将下方 **「可复制 Prompt」** 整段复制到 **新建的普通前台 Agent 对话** 中使用。不要用于 Multitask 或旧对话线程。

---

## 使用前检查清单

- [ ] 已完全退出并重启 Cursor（若近期刚批准 MCP）
- [ ] Settings → Tools & MCP 中 chrome-devtools、playwright、stitch 等为 ready
- [ ] **新建**普通前台 Agent 对话
- [ ] **已禁用 Multitask**
- [ ] 已运行 `npm run check:cursor-mcp`（CLI 参考；线程工具仍以对话为准）

---

## 可复制 Prompt

```
请在本仓库执行一轮 UI 实现（单一切片），严格遵守 Cursor 浏览器 UI 规范。

## 环境与约束

- 必须使用 **普通前台 Agent**；**禁止 Multitask** 与后台子 Agent。
- 任务开始前，先确认 **当前对话线程** 是否暴露以下 MCP 工具：stitch、chrome-devtools、playwright、filesystem、context7、github。
- 若当前线程缺少任一浏览器相关工具，立即输出 `BLOCKED: MISSING_FROM_THREAD_TOOL_REGISTRY` 并停止，不要假装截图或检查页面。
- **不改变业务逻辑**；每轮只改 **一个主要 UI 切片**。
- 本仓库为本地 Web 项目，**不得** 使用 wechat-chrome-session。

## 必读文档（按顺序）

1. README.md
2. AGENTS.md（含 Cursor Browser UI Workflow）
3. docs/STAGE_ROADMAP.md
4. docs/design/DESIGN.md
5. docs/design/stitch/UI_TASKS.md
6. docs/cursor_browser_ui_runbook.md

## 执行流程

1. 启动项目：`bash scripts/start_local.sh` 或等价命令。
2. 用 chrome-devtools 或 playwright 打开 Review 页（如 http://127.0.0.1:5173/?project_id=book_001&chapter_id=chapter_001）。
3. **Before**：截图 + 检查 console + 检查 network，记录 before 状态。
4. 读取 Stitch 设计（`docs/design/stitch/` 或调用 Stitch MCP）作为设计输入，**禁止**无审查覆盖业务代码。
5. 从 UI_TASKS 或 ROADMAP 中 **只选择一个 UI 切片** 实现。
6. 在 `apps/web/` 修改代码。
7. **After**：重新打开页面，截图 + console + network 检查。
8. 检查响应式（如需要）。
9. 运行测试：`npm run test`、`npm run build` 或 round 文档要求的验收命令。
10. 更新相关文档（若本轮有设计或任务状态变化）。
11. 汇报：before/after 截图路径、console/network 结论、修改文件列表、测试结果。
12. 仅在用户明确要求时 commit / push；提交前 `git diff` 确认无 .env、API Key、token。

## 本轮 UI 切片（请填写或让 Agent 从 UI_TASKS 中选一项）

<在此填写具体切片，例如：「Review 页波形区工具栏间距与对齐」>

## 验收标准

- 真实页面 before/after 已检查
- console 无未解释 error
- network 无异常失败请求
- 测试与 build 通过
- 业务功能（波形、切点、审核流程）未破坏
```

---

## 相关文件

- Runbook：[docs/cursor_browser_ui_runbook.md](../cursor_browser_ui_runbook.md)
- 线程检查：[docs/cursor_tool_registry_check.md](../cursor_tool_registry_check.md)
- MCP 检查：`npm run check:cursor-mcp`
