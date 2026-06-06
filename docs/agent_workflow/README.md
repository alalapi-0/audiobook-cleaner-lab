# Agent 工作流

## 阅读顺序

1. [README.md](../../README.md)
2. [AGENTS.md](../../AGENTS.md) / [agent.md](../../agent.md)
3. [PROJECT_STATE.md](../../PROJECT_STATE.md)
4. 当前 `rounds/round-XX-*.md`

## 任务类型与工具

| 任务类型 | 优先工具 / 文档 |
|----------|-----------------|
| UI 新页面 / 改版 | Stitch MCP → [docs/design/](../design/) → React 实现 |
| UI 验证 | Playwright / chrome-devtools → [BROWSER_TESTING.md](../testing/BROWSER_TESTING.md) |
| 真实 API | [REAL_API_TESTING.md](../testing/REAL_API_TESTING.md) |
| 用户验收 | Codex → [USER_PERSPECTIVE_TESTING.md](../testing/USER_PERSPECTIVE_TESTING.md) |
| MCP 配置 | [docs/mcp/](../mcp/)，`npm run check:mcp` |
| 库文档 | context7 |

## 标准推进轮

```bash
python3 scripts/check_repo.py
npm run check:mcp
npm run check:stitch   # 若涉及 Stitch
# ... 开发与专项测试 ...
python3 scripts/agent_gate.py
```

## UI 设计轮（含 Stitch）

1. 读 `docs/design/DESIGN.md` + `UI_TASKS.md`
2. Stitch 生成 → 保存 `exports/` / `screenshots/`
3. 拆任务 → `apps/web/` 实现
4. 浏览器验证 → 更新 `reviews/`

## 报告

每轮结束更新 `PROJECT_STATE.md`、`docs/governance/update_log.md`、对应 round 文件。
