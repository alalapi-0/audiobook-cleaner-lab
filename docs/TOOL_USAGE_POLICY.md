# 工具使用策略（Tool Usage Policy）

Date: 2026-06-09  
关联: `agent_tools.yaml`, `AGENTS.md`, `docs/SEARCH_POLICY.md`

## 1. 什么任务必须用什么工具

| 任务 | 必须 |
|------|------|
| 理解仓库结构 | 读 `AGENTS.md` + `agent_layer.yaml` + grep/glob |
| UI 改动验收 | Playwright CLI **或** playwright/chrome-devtools MCP + 截图 |
| 第三方库 API | context7 MCP **或** WebSearch 官方文档 |
| 修改 MCP 配置后 | `npm run check:mcp` + 重启 Cursor + 新对话 |
| 每轮结束 | `python3 scripts/agent_gate.py` + `reports/latest-agent-report.json` |
| mock 流水线验证 | `python3 scripts/auto_advance.py` 或 round 文档命令 |
| 真实 LLM | **禁止默认**；仅用户配置 Key + `real_api_check.py` 且非 gate 默认 |

## 2. 什么任务优先用什么工具

| 任务 | 优先 | 次选 |
|------|------|------|
| 代码定位 | Grep/Glob/Read | filesystem MCP |
| 小步修复 | Cursor Agent + shell | Codex |
| 大范围重构 | Codex handoff | Cursor 多轮 |
| 库文档 | context7 | WebSearch 官方站 |
| issue/PR 只读 | gh CLI | github MCP |
| UI 设计输入 | stitch MCP | `docs/design/` |
| 确定性回归 | `npm run test` | Playwright MCP |

## 3. 什么任务禁止用什么工具

| 禁止 | 原因 |
|------|------|
| 真实付费 ASR/LLM 于 gate/探针 | 成本与安全 |
| 修改 `.env` / 打印密钥 | 安全 |
| `git push --force` main | 破坏历史 |
| Stitch 导出无审查覆盖 `apps/web` | 质量风险 |
| wechat-chrome-session（本仓库） | 非微信项目 |
| Multitask 控制浏览器 | MCP 不继承 |
| 删除 `data/` 用户真实文件 | 数据丢失 |

## 4. 工具不可用时的 Fallback

| 工具 | Fallback |
|------|----------|
| playwright MCP | `cd apps/web && npm run test` |
| chrome-devtools MCP | Playwright + 手动浏览器 |
| context7 | WebSearch + 本地 docs |
| stitch MCP | `docs/design/DESIGN.md` |
| github MCP | `gh` / 仅本地 git |
| WebSearch | 记录 `TOOL_UNAVAILABLE_WEB_SEARCH`，请用户提供文档 |
| Codex | Cursor 小轮次 + `docs/CODEX_HANDOFF.md` |

记录 fallback 于 `reports/latest-agent-report.json` 的 `tools_used.fallback_used`。

## 5. Cursor 与 Codex 分工

| Cursor（主力） | Codex（高价值） |
|----------------|-----------------|
| 本地快速修复 | 大范围重构 |
| UI + Browser 调试 | 长程实现 |
| MCP 联动 | PR review |
| 文档/规则落地 | worktree 并行 |
| gate + 小轮次 | 难问题攻关 |

Codex 额度不足：**只用 Codex 做 Cursor 无法高效完成的高价值任务**。

## 6. MCP「配置了但不用」的避免

每轮在报告中填写：

- `tools_used` — 实际用了什么
- `tools_not_used` — 没用须说明原因（如「本轮无 UI 改动」）

UI 轮、审核台轮、发布预览轮：**必须**尝试 browser/playwright MCP 或 CLI 等价。

## 7. Web 搜索与过期知识

见 `docs/SEARCH_POLICY.md`。官方文档 > changelog > 官方 GitHub > 社区。

## 8. Browser / Playwright 用户视角

1. `bash scripts/start_local.sh`
2. 打开 Review URL
3. before：截图 + console + network
4. 改代码（小切片）
5. after：同上
6. `npm run test`
7. `python3 scripts/user_view_test.py`（服务已启动时）

## 9. 真实 API / 真实发布防误触发

- `agent_layer.yaml`: `allow_real_api: false`, `allow_real_publish: false`
- 导出默认 `--dry-run`
- `real_api_check.py` 无 Key 时 exit 2（跳过，非 gate 失败）
- 无「发布到平台」功能；未来若加须独立 env 开关

## 10. 每轮工具使用记录

写入 `reports/latest-agent-report.json` 并追加 `reports/agent_audit_log.jsonl`。

可选运行 `python3 scripts/tool_probe.py` 更新 `reports/tool_probe_report.json`。
