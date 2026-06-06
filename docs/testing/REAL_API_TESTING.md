# 真实 API 测试说明

## 原则

- 项目**支持**真实 LLM API 测试（OpenAI 兼容 Adapter）
- **无 Key 时**使用 mock / dry-run，**不得**将 mock 结果标注为 `real_api`
- 真实 API Key 仅存在于 `.env` 或环境变量，**不进 Git**

## 相关脚本

```bash
python3 scripts/real_api_check.py          # 真实 LLM 抽样验证
python3 scripts/run_llm_cut.py --engine openai  # 真实机切（需 Key）
python3 scripts/run_export.py --dry-run    # 导出干跑
```

## 环境变量

见 [`.env.example`](../../.env.example)：

- `LLM_API_KEY` / `OPENAI_API_KEY` / `OPENROUTER_API_KEY`
- 可选：`LLM_BASE_URL`、`LLM_MODEL`

Stitch 设计 API（独立）：

- `STITCH_API_KEY`

## 测试报告

- 真实 API 运行摘要可写入 `reports/real_api_runs/`（目录在 Git 中，大文件被 ignore）
- 报告中记录：模式（real_api / mock）、样本数、失败原因
- **禁止**在报告中粘贴完整 API Key

## 无 Key 时的行为

| 组件 | 行为 |
|------|------|
| `run_llm_cut.py` | 回退 mock Adapter |
| `real_api_check.py` | exit 2，0 次真实调用 |
| Stitch MCP | proxy 启动失败，提示设置 `STITCH_API_KEY` |

## Agent 要求

- 调用真实 API 前确认用户已授权本轮范围
- 在 round 报告中明确标注 `real_api` 或 `mock`
- 失败时保留日志摘要，不泄露密钥
