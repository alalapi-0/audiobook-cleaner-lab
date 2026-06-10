# AGENTS.md — AI Agent 工作规范

本文档面向后续在本仓库中工作的 AI Agent（**Cursor 主力**、Codex、Claude Code 等）。与 [agent_layer.yaml](agent_layer.yaml)、[agent_tools.yaml](agent_tools.yaml) 构成 **Tool-aware Agent Layer 2.0** 跨 Agent 协议。

## Repo Mission

个人有声书音频清洗与文本对齐剪辑：**原文 + ASR + LLM 机切建议 + 人工 Review + FFmpeg 导出**。默认 mock 流水线可端到端验收；真实付费 API 默认关闭。

## Agent 工作前读取顺序（Read First）

按优先级依次阅读，**不要无脑全量读取整个仓库**：

1. [AGENTS.md](AGENTS.md) — 本文档
2. [agent_tools.yaml](agent_tools.yaml) — 工具清单与可用性
3. [agent_layer.yaml](agent_layer.yaml) — 机器配置与命令
4. [docs/TOOL_USAGE_POLICY.md](docs/TOOL_USAGE_POLICY.md) — 工具使用策略
5. [docs/AGENT_RUNBOOK.md](docs/AGENT_RUNBOOK.md) — 轮次生命周期
6. [reports/latest-agent-report.json](reports/latest-agent-report.json) — 上一轮报告（若存在）
7. [README.md](README.md) — 项目目标与当前状态
8. [PROJECT_STATE.md](PROJECT_STATE.md) — 当前 Stage/Round 与风险
9. [docs/AGENT_ROADMAP.md](docs/AGENT_ROADMAP.md) — Agent 渐进轮（AL-01…）
10. [docs/governance/repo_protocol_standard.yaml](docs/governance/repo_protocol_standard.yaml) — 治理协议
11. [docs/governance/agent_reading_protocol.md](docs/governance/agent_reading_protocol.md) — 阅读策略
12. [docs/STAGE_ROADMAP.md](docs/STAGE_ROADMAP.md) — 业务 Stage 路线图
13. **当前 round 文件** — `rounds/round-XX-*.md`（业务轮）
14. 与本轮任务相关的设计文档与代码

**工具盘点**：开始前运行或读取 `python3 scripts/tool_probe.py` → [reports/tool_probe_report.json](reports/tool_probe_report.json)、[docs/TOOL_INVENTORY.md](docs/TOOL_INVENTORY.md)。

## Tool Inventory

见 [docs/TOOL_INVENTORY.md](docs/TOOL_INVENTORY.md) 与 [agent_tools.yaml](agent_tools.yaml)。MCP 已配置 6 个 server；**当前对话线程是否可调用须在工具列表中确认**。

## Tool Usage Policy

见 [docs/TOOL_USAGE_POLICY.md](docs/TOOL_USAGE_POLICY.md)。要点：UI 须 Browser/Playwright；库文档用 context7/WebSearch；每轮记录 `tool_usage`。

## Search Policy

见 [docs/SEARCH_POLICY.md](docs/SEARCH_POLICY.md)。依赖、工具能力、API、模型规则可能过期时**必须先搜索**；结果写入 [docs/RESEARCH_NOTES.md](docs/RESEARCH_NOTES.md)。

## Safe Operating Rules

见 [docs/AGENT_SAFETY.md](docs/AGENT_SAFETY.md)。`agent_layer.yaml`: `allow_real_api: false`, `allow_real_publish: false`。

## Round Lifecycle

见 [docs/AGENT_RUNBOOK.md](docs/AGENT_RUNBOOK.md)：读 → 探针 → 计划 → 搜索（若需）→ 实现 → gate → 用户视角（若 UI）→ 报告。

## Common Commands

```bash
python3 scripts/tool_probe.py
python3 scripts/check_repo.py
bash scripts/start_local.sh
python3 scripts/auto_advance.py
npm run check:mcp && npm run check:stitch
python3 scripts/agent_gate.py
python3 scripts/user_view_test.py   # 需服务运行
```

## Gate Commands

`python3 scripts/agent_gate.py` → [reports/gate_result.json](reports/gate_result.json)。提交前（若用户要求）须通过或记录失败原因。

## Severity Rules

| 级别 | 说明 |
|------|------|
| P0 | 数据丢失、密钥、无法启动、误发 API/发布 |
| P1 | 主流程不可用、核心测试失败 |
| P2 | 非核心、UI/UX |
| P3 | 文档、打磨 |

P0/P1 未清零不做 P2/P3。

## Report Format

Schema: [schemas/agent_round_report.schema.json](schemas/agent_round_report.schema.json)。输出: [reports/latest-agent-report.json](reports/latest-agent-report.json)，审计: [reports/agent_audit_log.jsonl](reports/agent_audit_log.jsonl)。规范: [docs/AGENT_REPORTING.md](docs/AGENT_REPORTING.md)。

## Cursor-specific Notes

- 主力 Agent；普通前台对话，**禁止 Multitask 控浏览器**
- 规则: `.cursor/rules/`（含 agent-layer、tool-usage、search-policy、safety-gates）
- MCP 批准后重启 Cursor + 新对话；见 [docs/cursor_tool_registry_check.md](docs/cursor_tool_registry_check.md)
- Prompt 模板: [docs/PROMPTS.md](docs/PROMPTS.md)

## Codex-specific Notes

- 启动前读本文 + [docs/CODEX_USAGE.md](docs/CODEX_USAGE.md)
- Handoff: [docs/CODEX_HANDOFF.md](docs/CODEX_HANDOFF.md)
- 额度有限：仅高价值任务；小修用 Cursor

## MCP-specific Notes

6 个 Workspace MCP（见下文 MCP Tools 章节）。探针禁止写操作/付费调用。不可用记 fallback。

## Browser / Playwright Notes

[docs/USER_VIEW_TESTING.md](docs/USER_VIEW_TESTING.md)、[docs/cursor_browser_ui_runbook.md](docs/cursor_browser_ui_runbook.md)。Review URL: `http://localhost:5173/?project_id=book_001&chapter_id=chapter_001`。

## Real API / Real Publish Rules

默认 mock；真实 LLM: `.env` + `real_api_check.py`；无社交平台自动发布。成本: [docs/COST_CONTROL.md](docs/COST_CONTROL.md)。

## Commit / Push Policy

仅用户明确要求时 commit；**默认不 push**；不提交 `.env`/密钥/真实素材。

## Next Round Policy

读 `latest-agent-report.json` → 选 [docs/AGENT_ROADMAP.md](docs/AGENT_ROADMAP.md) 下一 AL 条目 → 小范围 → gate → 报告。

## Human Required Decisions

配置 API Key、批准 MCP/重启 Cursor、扩大 round 范围、force push、删除 data 用户文件。

## 禁止事项

- **禁止**读取或提交 `.env`、API Key、Token、密码
- **禁止**把真实音频、真实小说文本提交到 Git
- **禁止**在本轮未授权范围内调用真实付费 ASR/LLM API
- **禁止**处理用户真实素材（除非用户在本轮明确提供路径并授权）
- **禁止**删除 `data/` 中用户已有的真实文件
- **禁止**让大模型直接切音频（仅允许文本层机切建议）
- **禁止**覆盖原始音频文件
- **禁止**未经用户明确要求就 `git push`
- **禁止**无脑全量扫描 `data/`、`.git/`、`node_modules/` 等大目录

## 每轮推进规则

每一轮必须明确：

- 本轮目标、产物、不做什么
- 验收命令或验收方式
- 下一轮入口

每轮完成后**必须更新**：

- [PROJECT_STATE.md](PROJECT_STATE.md)
- [docs/governance/update_log.md](docs/governance/update_log.md)
- 对应 `rounds/round-XX-*.md`（标记完成状态）
- 若治理规则变更：同步 [docs/governance/repo_protocol_standard.yaml](docs/governance/repo_protocol_standard.yaml)

## 如何处理 data 目录

- `data/` 是本地工作区，真实内容**不进 Git**
- 可用 `python scripts/init_data_dirs.py` 初始化子目录
- Agent 只读写 schema 示例路径，不假设用户素材已存在
- 扫描时用 glob 定位具体 JSON，不要 `read` 整个 data 树

## 如何处理用户真实素材

- 默认不访问、不复制、不上传
- 若用户在本轮提供路径，仅读取本轮任务所需的最小文件
- 不得在仓库中生成或提交真实音频副本

## 如何处理既有协议文件

- 权威协议位于 `docs/governance/repo_protocol_standard.yaml`
- 参考来源：`novel-continuation-agent/governance/repo_protocol_standard.yaml`
- 冲突时以**当前 Round Prompt** 为准
- 协议变更须写入 `update_log.md`

## 如何避免无脑全量读取

1. 先读固定入口文件（见上方读取顺序前 7 项）
2. 用 grep/glob 定位相关文件
3. 大文件（>1MB）先查路径与标题，再 targeted read
4. 跳过 `.git/`、`node_modules/`、`data/**` 二进制、`__pycache__/`
5. 不确定时写 TODO，**不要乱实现**

## 如何在不确定时行动

- 在文档或代码中标注「当前默认假设」
- 在 round 文件或 PROJECT_STATE 中记录 open question
- 不擅自扩大 Round 范围

## 每轮最终报告格式

完成一轮后，用中文汇报：

1. 读取并参考了哪些文件
2. 本轮做了什么
3. 创建/修改了哪些文件
4. 本轮没有做什么
5. 验收命令与结果
6. 当前仓库状态
7. 下一轮建议
8. 风险或 TODO

## 验收脚本

```bash
python scripts/check_repo.py      # 仓库骨架检查
python scripts/init_data_dirs.py  # 初始化 data 子目录（首次或重置结构时）
```

业务 Round 完成后还应运行该 Round 文档中声明的专项测试。

## MCP Tools

当前项目要求启用以下 **Workspace MCP Servers**（见 [`.cursor/mcp.json`](.cursor/mcp.json)）：

| MCP | 用途 |
|-----|------|
| **chrome-devtools** | 浏览器调试、console、network、页面状态检查 |
| **context7** | 查询第三方库和框架文档 |
| **filesystem** | 安全读取和检查当前项目文件（仅 `${workspaceFolder}`） |
| **github** | 仓库、提交、分支、issue、PR 等相关操作 |
| **playwright** | 浏览器自动化、页面操作、E2E 检查 |
| **stitch** | UI 设计、原型、截图、HTML 导出（需 `STITCH_API_KEY`） |

**自动推进轮开始前**，Agent 必须确认上述 MCP 已在 Cursor Settings → MCP 中加载。若某个 MCP 不可用，须记录原因并使用可用替代方案继续推进（见 [docs/agent_skills/mcp_usage_skill.md](docs/agent_skills/mcp_usage_skill.md)）。

涉及页面、审核台、生成结果、预览、发布流程的任务，**必须**使用 **chrome-devtools** 或 **playwright** 进行真实浏览器检查（页面、console、network、核心流程），不得仅凭代码静态阅读判断成功。

| 原则 | 说明 |
|------|------|
| 加载确认 | 修改 `.cursor/mcp.json` 后需 **重启 Cursor 或 Reload Window** |
| 文件操作 | 必须确认真实文件状态；filesystem 仅授权当前项目目录 |
| GitHub | 提交 / push 前必须 `git diff`，避免泄露密钥；token 仅通过环境变量提供 |
| MCP 不可用 | 记录原因并降级，不要无意义反复安装 |
| 缺少 token | 进入 mock / dry-run，**不要卡死**整体流程（除非 token 是唯一阻塞） |

检查命令：

```bash
node scripts/check_mcp_config.js   # MCP 配置格式与安全检查（Node.js）
npm run check:mcp                  # 同上（根 package.json 别名）
npm run check:stitch               # Stitch 专项配置与安全检查
python3 scripts/check_mcp_config.py  # Python 等价检查（可选）
```

详细说明见 [docs/agent_skills/mcp_usage_skill.md](docs/agent_skills/mcp_usage_skill.md) 与 [docs/agent-browser-verification.md](docs/agent-browser-verification.md)。

## Stitch Design MCP

1. 本项目可使用 **Stitch** 作为 UI 设计工具（MCP server 名称：`stitch`）。

2. 涉及 **UI、页面、审核台、预览页、管理后台、视觉检查页** 时，Agent 应优先查看：

   - [docs/design/DESIGN.md](docs/design/DESIGN.md)
   - [docs/design/stitch/README.md](docs/design/stitch/README.md)
   - [docs/design/stitch/UI_TASKS.md](docs/design/stitch/UI_TASKS.md)
   - [docs/design/stitch/PROMPT_TEMPLATES.md](docs/design/stitch/PROMPT_TEMPLATES.md)

3. 若 Stitch MCP 可用，Agent 可以用 Stitch 生成：UI 原型、screen、screenshot、HTML、DESIGN.md、多方案 variants。

4. Stitch 生成结果必须保存到：

   - `docs/design/stitch/exports/`
   - `docs/design/stitch/screenshots/`
   - `docs/design/stitch/reviews/`

5. Agent **不得**把 Stitch 导出的代码无审查地覆盖项目代码。

6. Agent 实现 UI 前必须把 Stitch 结果拆成可落地任务。

7. Agent 实现 UI 后**必须**使用 Playwright 或 chrome-devtools 检查。

8. 若 Stitch MCP 不可用，Agent 应记录原因，并使用文档模板继续推进。

配置详见 [docs/design/stitch/STITCH_MCP_SETUP.md](docs/design/stitch/STITCH_MCP_SETUP.md)。

## Cursor Browser UI Workflow

Cursor 在本仓库做 UI 优化时，必须遵守以下规则（详见 [docs/cursor_browser_ui_runbook.md](docs/cursor_browser_ui_runbook.md) 与 [docs/cursor_tool_registry_check.md](docs/cursor_tool_registry_check.md)）：

1. **必须使用普通前台 Agent**；批准 MCP 或修改配置后应完全退出 Cursor、重开仓库、**新建对话**。
2. **禁止 Multitask 控制浏览器**；子 Agent 可能未继承 Workspace MCP（见 `.cursor/rules/no-multitask-for-browser.mdc`）。
3. **每轮 UI 实现必须先检查真实页面**（chrome-devtools 或 playwright），不得仅凭代码静态阅读。
4. **每轮 UI 实现必须进行 before / after 浏览器检查**（截图、console、network）。
5. **Stitch 用作设计输入**；导出物存 `docs/design/stitch/`，禁止无审查覆盖业务代码。
6. **chrome-devtools 用作页面调试**（console、network、截图、DOM）。
7. **playwright 用作回归测试**与稳定 E2E 验收。
8. **filesystem 用作文件真值检查**（仅 `${workspaceFolder}`）。
9. **context7 用作文档查询**（React、Vite、wavesurfer 等）。
10. **github 用作提交和远程状态**（token 仅环境变量，提交前 `git diff`）。
11. **微信已登录页面**（其他项目）只允许 `wechat-chrome-session`；**本仓库为本地 Web，不得使用 wechat-chrome-session**。
12. **若当前对话线程缺工具**，输出 `BLOCKED: MISSING_FROM_THREAD_TOOL_REGISTRY` 并停止，不要假装执行浏览器检查。

检查命令：

```bash
npm run check:cursor-mcp   # CLI 层 MCP（不代表当前线程）
npm run check:mcp
npm run check:stitch
```

UI 推进 Prompt 模板：[docs/prompts/CURSOR_UI_IMPLEMENTATION_PROMPT.md](docs/prompts/CURSOR_UI_IMPLEMENTATION_PROMPT.md)。
