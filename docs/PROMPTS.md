# Agent Prompt 模板

每模板均要求：先读 AGENTS.md、agent_tools.yaml、latest-agent-report → 判断搜索与工具 → 小任务 → gate → 报告 → 记录 tool_usage → 无真实发布/付费 API → 无自动 push。

---

## 1. Cursor 工具盘点轮

```
你是 audiobook-cleaner-lab 的 Tool-aware Agent。
先读：AGENTS.md、agent_tools.yaml、agent_layer.yaml、reports/latest-agent-report.json。
运行：python3 scripts/tool_probe.py
更新：docs/TOOL_INVENTORY.md、agent_tools.yaml（若有变更）
判断：当前线程 MCP 是否可调用；不可调用记 tools_not_used + fallback。
禁止：付费 API、push、改 .env。
结束：python3 scripts/agent_gate.py（或记录 BLOCKED）、更新 reports/latest-agent-report.json。
```

## 2. Cursor 小步实现轮

```
先读 AGENTS.md、agent_tools.yaml、docs/AGENT_ROADMAP.md 中本轮 AL-XX、latest-agent-report.json。
本轮只做 roadmap 中一个 AL 条目的 scope，不扩大。
实现前：grep/glob 定位；若 API/依赖不确定则 WebSearch 官方文档并写 RESEARCH_NOTES。
实现后：python3 scripts/agent_gate.py。
报告：latest-agent-report.json + tool_usage。
禁止：真实 API、push、覆盖 data/ 原音频。
```

## 3. Cursor 用户视角测试轮

```
先读：AGENTS.md、docs/USER_VIEW_TESTING.md、docs/cursor_browser_ui_runbook.md。
启动：bash scripts/start_local.sh
工具：优先 playwright MCP 或 chrome-devtools；不可用则 npm run test + user_view_test.py。
流程：before 截图/console/network → 检查清单 → after 对比。
禁止：Multitask 控浏览器。
结束：gate + 报告，注明 Browser MCP 是否使用。
```

## 4. Cursor P0/P1 修复轮

```
先读：latest-agent-report.json、reports/gate_result.json、PROJECT_STATE.md。
只修 P0/P1；不修 P2/P3 打磨。
定位：失败测试/日志 → 最小修复。
验证：agent_gate + 失败用例专项。
报告：severity_summary 更新。
```

## 5. Codex 高价值 handoff Prompt

```
Codex：读取 docs/CODEX_HANDOFF.md（已由 Cursor 填写）及 AGENTS.md、agent_layer.yaml、agent_tools.yaml。
任务：handoff 中 Current goal（单任务）。
约束：no real API、no publish、no push。
运行：handoff 中 Commands。
返回：Return format 章节要求的内容 + 更新 latest-agent-report.json。
```

## 6. Codex Review Prompt

```
Codex Review 模式：读取 git diff（不 push）。
参考：AGENTS.md、docs/governance/repo_protocol_standard.yaml。
输出：P0/P1/P2/P3 问题列表、建议修复顺序。
不自动改代码除非 handoff 明确要求。
记录：web_research 若查了 API 文档。
```

## 7. Web Research Prompt

```
先读 docs/SEARCH_POLICY.md。
搜索：[具体 Query] — 优先官方文档。
写入 docs/RESEARCH_NOTES.md（日期、来源类型、不确定性）。
若无法搜索：记录 TOOL_UNAVAILABLE_WEB_SEARCH。
将可执行结论编码到指定文件（AGENTS.md / runbook / 代码注释仅必要时）。
```

## 8. MCP Probe Prompt

```
先读 agent_tools.yaml、.cursor/mcp.json、docs/TOOL_INVENTORY.md。
对每个 MCP：仅只读 safe_probe（list tools、读 README、npm run check:mcp）。
禁止：写操作、发布、删数据、付费 API。
更新：reports/tool_probe_report.json、docs/TOOL_INVENTORY.md callable_now 字段。
线程无 MCP：输出 BLOCKED: MISSING_FROM_THREAD_TOOL_REGISTRY。
结束：latest-agent-report.json 记录 tools_used/tools_not_used。
```
