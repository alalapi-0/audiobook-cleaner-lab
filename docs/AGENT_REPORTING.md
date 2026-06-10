# Agent 报告规范（Reporting）

## Schema

`schemas/agent_round_report.schema.json`

## 输出文件

| 文件 | 用途 |
|------|------|
| `reports/latest-agent-report.json` | 下一轮 Agent 入口 |
| `reports/agent_audit_log.jsonl` | 历史审计（每行一条 JSON） |
| `reports/gate_result.json` | 门禁结果 |
| `reports/tool_probe_report.json` | 工具探针 |

## 必填字段摘要

- `round_id`, `timestamp`, `agent`, `agent_surface`, `mode`, `goal`
- `tools_used` / `tools_not_used`（**每轮必填**）
- `web_research`（若搜索过）
- `gate_status`, `severity_summary`
- `next_recommended_round`

## tool_usage 规则

- 工具可用但没用 → `tools_not_used` 写原因
- 用了 fallback → `tools_used.fallback_used: true`

## 追加 audit log

```bash
# Agent 在轮末将 latest-agent-report.json 单行追加到：
# reports/agent_audit_log.jsonl
```

## 与 PROJECT_STATE 的关系

- **Agent Layer 轮**：以 `latest-agent-report.json` 为主
- **业务 Round**：还须更新 `PROJECT_STATE.md` 与 `rounds/`
