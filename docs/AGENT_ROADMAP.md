# Agent 渐进式 Roadmap（Layer 2.0+）

与业务 `docs/STAGE_ROADMAP.md` / `rounds/` 互补。每轮：**小范围、有 gate、有报告、有工具绑定**。

---

## Phase 0 — 仓库事实层

### AL-01
- **title**: 仓库事实扫描固化
- **goal**: 更新 file_role_map 与 README 导航
- **why_now**: Layer 2.0 基线
- **scope**: docs/governance, README
- **likely_files**: `docs/governance/file_role_map.yaml`, `README.md`
- **tools_to_use**: shell, grep
- **tools_to_probe**: git
- **web_search_needed**: false
- **commands_to_run**: `python3 scripts/check_repo.py`
- **acceptance_criteria**: check_repo 通过
- **risks**: 与 governance 冲突
- **fallback**: 以 repo_protocol_standard.yaml 为准
- **depends_on**: agent-layer-2.0-bootstrap

### AL-02
- **title**: data/ 目录 schema 示例补齐
- **goal**: 确保 init_data_dirs 覆盖全部 JSON 路径
- **scope**: scripts/, data/
- **tools_to_use**: shell, filesystem
- **tools_to_probe**: python
- **web_search_needed**: false
- **commands_to_run**: `python3 scripts/init_data_dirs.py`
- **acceptance_criteria**: 示例 manifest 可读
- **risks**: 误删用户 data
- **fallback**: 只创建缺失目录
- **depends_on**: AL-01

---

## Phase 1 — 工具盘点层

### AL-03
- **title**: 工具探针 CI 化
- **goal**: CI 或 pre-commit 运行 tool_probe
- **scope**: scripts/, .github/ 或 docs
- **tools_to_use**: shell
- **tools_to_probe**: all binaries
- **web_search_needed**: false
- **commands_to_run**: `python3 scripts/tool_probe.py`
- **acceptance_criteria**: tool_probe_report.json 更新
- **risks**: CI 无 ffmpeg
- **fallback**: 标记 BLOCKED_ENV
- **depends_on**: agent-layer-2.0-bootstrap

### AL-04
- **title**: MCP 线程注册表自检文档化
- **goal**: 更新 cursor_tool_registry_check 与 TOOL_INVENTORY
- **scope**: docs/
- **tools_to_use**: Read, npm run check:mcp
- **tools_to_probe**: MCP panel（人工）
- **web_search_needed**: true（Cursor MCP 变更时）
- **commands_to_run**: `npm run check:cursor-mcp`
- **acceptance_criteria**: 文档含 BLOCKED 流程
- **risks**: Cursor 版本差异
- **fallback**: 手动确认清单
- **depends_on**: AL-03

---

## Phase 2 — 搜索与文档更新层

### AL-05
- **title**: FastAPI/Pydantic 版本备忘
- **goal**: RESEARCH_NOTES 记录当前依赖 API
- **scope**: docs/RESEARCH_NOTES.md
- **tools_to_use**: web_search, context7
- **tools_to_probe**: context7
- **web_search_needed**: true
- **commands_to_run**: pytest API tests
- **acceptance_criteria**: RESEARCH_NOTES 有 dated entry
- **risks**: Python 3.14 兼容性
- **fallback**: 锁定 pyproject 版本说明
- **depends_on**: AL-04

### AL-06
- **title**: Playwright 配置与官方文档对齐
- **goal**: 核对 playwright.config 与最新 API
- **scope**: apps/web/
- **tools_to_use**: web_search, playwright CLI
- **tools_to_probe**: playwright MCP
- **web_search_needed**: true
- **commands_to_run**: `cd apps/web && npm run test`
- **acceptance_criteria**: E2E 绿
- **risks**: webServer 超时
- **fallback**: 延长 timeout
- **depends_on**: AL-05

---

## Phase 3 — Agent 规则层

### AL-07
- **title**: Cursor rules 与 AGENTS.md 交叉引用审计
- **goal**: 消除重复/冲突规则
- **scope**: .cursor/rules/, AGENTS.md
- **tools_to_use**: grep
- **web_search_needed**: false
- **commands_to_run**: 人工 diff
- **acceptance_criteria**: AGENT_LAYER_AUDIT 更新
- **depends_on**: agent-layer-2.0-bootstrap

### AL-08
- **title**: browser-debug-check Skill 增强
- **goal**: 链接 USER_VIEW_TESTING 步骤
- **scope**: .cursor/skills/
- **tools_to_use**: Read/Write
- **depends_on**: AL-07

---

## Phase 4 — 门禁脚本层

### AL-09
- **title**: agent_gate 纳入 tool_probe 可选步骤
- **goal**: gate_result 含 probe 摘要
- **scope**: scripts/agent_gate.py
- **tools_to_use**: shell
- **commands_to_run**: `python3 scripts/agent_gate.py`
- **acceptance_criteria**: gate_result.json 完整
- **depends_on**: AL-03

### AL-10
- **title**: pytest 覆盖率基线
- **goal**: 记录 packages/ 测试缺口
- **scope**: tests/
- **tools_to_use**: pytest
- **commands_to_run**: `python3 -m pytest tests/ -v`
- **depends_on**: AL-09

---

## Phase 5 — 报告与审计层

### AL-11
- **title**: audit_log 轮转策略
- **goal**: 文档化 jsonl 大小与归档
- **scope**: docs/AGENT_REPORTING.md
- **depends_on**: agent-layer-2.0-bootstrap

### AL-12
- **title**: round report 校验脚本
- **goal**: JSON Schema validate latest report
- **scope**: scripts/, schemas/
- **tools_to_use**: python jsonschema（若引入）
- **depends_on**: AL-11

---

## Phase 6 — 用户视角测试层

### AL-13
- **title**: user_view_test 集成 Playwright 子集
- **goal**: 单命令用户视角报告
- **scope**: scripts/user_view_test.py
- **tools_to_use**: playwright CLI
- **commands_to_run**: `python3 scripts/user_view_test.py`
- **depends_on**: AL-06

### AL-14
- **title**: Review 页 E2E 扩展（空状态）
- **goal**: 覆盖无 chapter / 404 路由
- **scope**: apps/web/tests/
- **tools_to_use**: playwright
- **depends_on**: AL-13

### AL-15
- **title**: 波形编辑器交互 E2E
- **goal**: 切点选择 smoke
- **scope**: apps/web/tests/
- **tools_to_use**: playwright MCP 或 CLI
- **depends_on**: AL-14

---

## Phase 7 — 核心功能稳定层

### AL-16
- **title**: auto_advance 与 gate 联合 smoke
- **goal**: gate 前可选 dry auto_advance
- **scope**: scripts/
- **commands_to_run**: `python3 scripts/auto_advance.py`
- **depends_on**: AL-10

### AL-17
- **title**: Review API 契约测试补强
- **goal**: review.py 边界 case
- **scope**: tests/test_review_api.py
- **depends_on**: AL-16

### AL-18
- **title**: 对齐算法回归样本
- **goal**: fixtures + 对齐 golden
- **scope**: tests/, data/fixtures
- **depends_on**: AL-17

---

## Phase 8 — P0/P1 自动修复闭环

### AL-19
- **title**: gate 失败分类器
- **goal**: gate_result next_action 枚举扩展
- **scope**: scripts/agent_gate.py
- **depends_on**: AL-09

### AL-20
- **title**: Manifest 404 UX 回归
- **goal**: 确保错误 chapter 友好提示
- **scope**: apps/api, apps/web
- **tools_to_use**: playwright
- **depends_on**: AL-19

---

## Phase 9 — UI/UX 质量审核层

### AL-21
- **title**: Stitch → Review 设计 diff 记录
- **goal**: reviews/ 目录有本轮记录
- **scope**: docs/design/stitch/
- **tools_to_use**: stitch MCP
- **tools_to_probe**: stitch
- **depends_on**: AL-08

### AL-22
- **title**: 移动端窄屏截图基线
- **goal**: screenshots/ 存基线
- **tools_to_use**: chrome-devtools, playwright
- **depends_on**: AL-21

### AL-23
- **title**: a11y 基础检查（文案/焦点）
- **goal**: 清单项记入 USER_VIEW_TESTING
- **scope**: docs/, apps/web
- **depends_on**: AL-22

---

## Phase 10 — mock / dry-run / real API 分离层

### AL-24
- **title**: real_api_check 报告标准化
- **goal**: reports/real_api_runs/ schema
- **scope**: scripts/real_api_check.py
- **depends_on**: AL-16

### AL-25
- **title**: Round 13 R2 真实 LLM 验收
- **goal**: 用户 Key 后 pipeline 真实调用
- **scope**: packages/llm_core/
- **tools_to_use**: real_api_check（显式）
- **web_search_needed**: true（模型 API）
- **depends_on**: AL-24, 用户 LLM_API_KEY

### AL-26
- **title**: ASR 真实 Adapter 骨架
- **goal**: 与 mock 并行 adapter 接口
- **scope**: packages/asr_core/
- **web_search_needed**: true
- **depends_on**: AL-25

---

## Phase 11 — 成本控制层

### AL-27
- **title**: batch 成本估算字段
- **goal**: manifest 记录 token/字符估算
- **scope**: packages/, docs/COST_CONTROL.md
- **depends_on**: AL-25

### AL-28
- **title**: Stitch 调用次数日志
- **goal**: 本地 ledger 不入 Git
- **scope**: reports/
- **depends_on**: AL-21

---

## Phase 12 — Codex handoff 层

### AL-29
- **title**: 首次 Codex handoff 演练
- **goal**: 填 CODEX_HANDOFF 完成小任务
- **scope**: docs/CODEX_HANDOFF.md
- **tools_to_use**: Codex（manual）
- **depends_on**: agent-layer-2.0-bootstrap

### AL-30
- **title**: Codex review 模板实战
- **goal**: 用 Codex Review Prompt 审一轮 diff
- **scope**: docs/PROMPTS.md
- **depends_on**: AL-29

---

## Phase 13 — Cursor 主力小轮次推进层

### AL-31
- **title**: ImportGuide 用户流程 E2E
- **goal**: 新用户导入指引可点击
- **scope**: apps/web/
- **tools_to_use**: playwright
- **depends_on**: AL-15

### AL-32
- **title**: ExportGuide dry-run 文案对齐
- **goal**: 与 run_export --dry-run 一致
- **scope**: apps/web/, docs/
- **depends_on**: AL-31

### AL-33
- **title**: batch_process 断点续跑文档+测试
- **goal**: 中断后恢复章节
- **scope**: scripts/batch_process.py
- **depends_on**: AL-18

---

## Phase 14 — Cloud / multi-agent 可选层

### AL-34
- **title**: Cursor Cloud Agent 适用性评估
- **goal**: RESEARCH_NOTES + RUNBOOK 章节
- **web_search_needed**: true
- **depends_on**: AL-04

### AL-35
- **title**: Subagents 任务拆分试点
- **goal**: 只读审查子任务
- **tools_to_use**: Task/subagent（若可用）
- **depends_on**: AL-34

---

## Phase 15 — 长期维护与 CI 层

### AL-36
- **title**: GitHub Actions agent_gate
- **goal**: PR 上运行 pytest + agent:check
- **scope**: .github/workflows/
- **tools_to_use**: gh, shell
- **depends_on**: AL-09

### AL-37
- **title**: Dependabot / 依赖安全扫描
- **goal**: npm + pip 审计策略
- **web_search_needed**: true
- **depends_on**: AL-36

### AL-38
- **title**: 季度工具盘点自动化
- **goal**: tool_probe 定时 + TOOL_INVENTORY 模板
- **depends_on**: AL-03

### AL-39
- **title**: governance update_log 与 Agent 报告合并索引
- **goal**: 单一导航页
- **scope**: docs/governance/
- **depends_on**: AL-11

### AL-40
- **title**: Layer 3.0 差距评估
- **goal**: AGENT_LAYER_AUDIT 下一轮规划
- **depends_on**: AL-38, AL-39

---

## 下一轮推荐

**AL-03**（工具探针 CI 化）或 **AL-13**（用户视角测试增强），取决于是否优先 UI 稳定。
