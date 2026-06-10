# 成本控制（Cost Control）

本项目涉及潜在付费：ASR API、LLM API、Stitch API。

## 默认策略

| 组件 | 默认 | 控制手段 |
|------|------|----------|
| ASR | mock | `packages/asr_core` mock adapter |
| LLM 机切 | mock | `packages/llm_core` mock adapter |
| Stitch | 可选 | 无 `STITCH_API_KEY` 时跳过 MCP |
| Gate/探针 | 零付费 | 不调用真实 API |

## 真实 API 启用条件

1. 用户在 `.env` 配置 Key（不进 Git）
2. 显式运行 `real_api_check.py` 或业务脚本带真实 flag
3. 记录成本相关元数据到 `reports/real_api_runs/`

## Agent 规则

- gate **不**调用真实 API
- 文档润色、小修小补 **不**使用 Codex 付费额度（优先 Cursor）
- 大批量章节处理前建议用户确认 `--dry-run` / mock 样本

## 断点与估算

- `batch_process.py` 支持按章节处理
- 未来 round：token/字符数 ledger（见 `AGENT_ROADMAP.md` Phase 11）

## Fallback

无 Key → mock 链路 + `PROJECT_STATE` 记录「非硬阻塞」
