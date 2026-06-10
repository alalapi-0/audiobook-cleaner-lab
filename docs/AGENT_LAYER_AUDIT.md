# Agent Layer 2.0 审计（本轮）

Date: 2026-06-09  
Round: agent-layer-2.0-bootstrap

## 已有资产（保留并整合）

| 资产 | 状态 |
|------|------|
| AGENTS.md | 已补强 Layer 2.0 章节 |
| agent.md | 保留，指向 AGENTS.md |
| docs/governance/repo_protocol_standard.yaml | 保留，权威治理 |
| scripts/agent_gate.py | 增强：Layer 文件检查 + gate_result.json |
| .cursor/mcp.json（6 MCP） | 保留 |
| .cursor/rules/（6+5 规则） | 补强 |
| docs/agent_workflow/ | 保留 |
| docs/testing/* | 保留 |
| rounds/ + STAGE_ROADMAP | 保留，与 AGENT_ROADMAP 互补 |

## 本轮新增

| 文件 | 用途 |
|------|------|
| agent_layer.yaml | 机器可读层配置 |
| agent_tools.yaml | 工具清单 |
| docs/TOOL_* | 盘点与策略 |
| docs/SEARCH_POLICY.md | 搜索策略 |
| docs/AGENT_ROADMAP.md | 20–40 渐进轮 |
| docs/PROMPTS.md | Prompt 模板 |
| schemas/agent_round_report.schema.json | 报告 schema |
| scripts/tool_probe.py | 工具探针 |
| scripts/user_view_test.py | 用户视角探针 |
| reports/* | 结构化报告 |

## 冲突处理

- `docs/STAGE_ROADMAP.md` = 业务 Stage 0–11（已完成）
- `docs/AGENT_ROADMAP.md` = Agent Layer + 后续能力渐进轮
- 治理优先级仍以 `repo_protocol_standard.yaml` 为准

## 缺口（后续 round）

- CI 中运行 agent_gate
- token/cost ledger 自动化
- MCP callable_now 自动检测（需 Cursor API）
- 真实 ASR Adapter（业务 round）
