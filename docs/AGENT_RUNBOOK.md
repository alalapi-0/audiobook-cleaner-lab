# Agent Runbook

每轮 Agent 的标准操作手册。与 `AGENTS.md`、`agent_layer.yaml` 配套。

## 轮次生命周期（Round Lifecycle）

1. **读** — `AGENTS.md` → `agent_tools.yaml` → `agent_layer.yaml` → `reports/latest-agent-report.json` → 本轮 roadmap 条目
2. **探针** — `python3 scripts/tool_probe.py`（或读最近 `reports/tool_probe_report.json`）
3. **计划** — 确认本轮工具、命令、范围（小任务）
4. **搜索** — 若涉及新 API/工具能力 → `docs/SEARCH_POLICY.md`
5. **实现** — 最小 diff
6. **验证** — gate + 专项测试 + 用户视角（若 UI）
7. **报告** — `reports/latest-agent-report.json` + audit log
8. **更新** — `PROJECT_STATE.md`（若业务 round 完成）

## 必读文件（Read First）

见 `agent_layer.yaml` → `docs.read_first`。

## 常用命令

```bash
# 环境
python3 scripts/check_environment.py
python3 scripts/init_data_dirs.py
python3 scripts/check_repo.py

# 启动
bash scripts/start_local.sh

# Mock 流水线
python3 scripts/auto_advance.py

# MCP 检查
npm run check:mcp
npm run check:stitch
npm run check:cursor-mcp

# 工具探针
python3 scripts/tool_probe.py

# 门禁
python3 scripts/agent_gate.py

# 用户视角（需服务运行）
python3 scripts/user_view_test.py

# 真实 API（非默认）
python3 scripts/real_api_check.py
```

## Gate 命令

`python3 scripts/agent_gate.py` 输出 `reports/gate_result.json`。

通过标准：Agent Layer 文件齐全 + check_repo + check_environment + compileall + pytest + npm agent:check。

## 严重级别（Severity）

| 级别 | 定义 |
|------|------|
| P0 | 数据丢失、密钥泄露、无法启动、破坏性行为、误发 API/发布 |
| P1 | 主流程不可用、核心测试失败 |
| P2 | 非核心功能、UI/UX 缺陷 |
| P3 | 文档、重构、打磨 |

**P0/P1 未清零不做 P2/P3 优化。**

## Commit / Push

- 仅用户明确要求时 commit
- 默认不 push
- 提交前须 gate 通过（或记录失败原因）

## 人类必须决策项

- 配置真实 ASR/LLM API Key
- 批准 MCP / 重启 Cursor
- force push / 删除 data 用户文件
- 扩大 round 范围超出 roadmap

## 相关文档

- [TOOL_USAGE_POLICY.md](TOOL_USAGE_POLICY.md)
- [AGENT_ROADMAP.md](AGENT_ROADMAP.md)
- [AGENT_REPORTING.md](AGENT_REPORTING.md)
- [USER_VIEW_TESTING.md](USER_VIEW_TESTING.md)
- [CODEX_USAGE.md](CODEX_USAGE.md)
