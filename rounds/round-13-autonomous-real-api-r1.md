# Round 13 — Autonomous Real API Round 1

## 目标

接入真实 OpenAI 兼容 LLM API，生成 ≥3 个真实机切样本并评估质量。

## 状态

**硬阻塞（HARD_BLOCK）** — 未检测到 API Key，无法发起真实 API 调用。

## 本轮做了什么

1. 新增 `OpenAiCompatibleAdapter`（httpx + Chat Completions JSON mode）
2. 新增 `LlmApiConfig` 与 `.env` 加载（不输出密钥）
3. 新增 `scripts/real_api_check.py` — 3 个独立测试场景 + 报告写入
4. 新增 `prompts/llm_cut_decision/system_openai.md`
5. 新增 `.env.example` 配置模板
6. `run_llm_cut.py` 支持 `--engine openai`
7. 报告目录 `reports/real_api_runs/`

## 验收

```bash
.venv/bin/python scripts/real_api_check.py   # exit 2 = 无 API Key
.venv/bin/python scripts/agent_gate.py         # 通过
.venv/bin/python -m unittest tests.test_llm_cut_decision -v  # 4 tests OK
```

## 真实 API 调用

- **调用次数**: 0（硬阻塞）
- **报告路径**: `reports/real_api_runs/20260531T230945Z/report.json`

## 阻塞原因

`LLM_API_KEY` / `OPENAI_API_KEY` 未在环境变量或 `.env` 中配置。

## 解除阻塞

```bash
cp .env.example .env
# 编辑 .env 填入 LLM_API_KEY
.venv/bin/python scripts/real_api_check.py --pipeline
```

## 下一轮

Round 2 需在 `.env` 配置 API Key 后重新运行 `real_api_check.py`。
