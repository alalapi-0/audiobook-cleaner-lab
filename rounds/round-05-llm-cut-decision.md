# Round 05 — 大模型机切建议

**状态：已完成（2026-05-27）**

## Round 目标

实现 `LLM_CUT_DECISION_PROTOCOL` 与 `MockLlmAdapter`，输出 `llm_cut_decision.json`。

## 前置条件

Round 04 alignment 可用。

## 主要任务

- Prompt 模板 `prompts/llm_cut_decision/`
- `MockLlmAdapter` 按规则输出 JSON
- 校验 action / reason_type / confidence 规则
- **明确：不直接切音频**

## 输出文件

- `packages/llm_core/adapters/mock.py`
- `llm_cut_decision.json` schema 校验

## 验收标准

- mock 输出通过 schema
- confidence < 0.75 不单独 auto delete
- uncertain 条目存在

## 不做什么

- 不接真实付费 LLM API
- 不执行 FFmpeg

## 完成记录

- [x] `packages/llm_core/adapters/mock.py` — MockLlmAdapter
- [x] `packages/llm_core/service.py` — LlmCutService
- [x] `prompts/llm_cut_decision/system_mock.md`
- [x] `scripts/run_llm_cut.py`
- [x] `tests/test_llm_cut_decision.py` — 4 项测试

## 验收结果

```bash
python3 -m unittest tests.test_llm_cut_decision -v  # 4 tests OK
```

## 下一轮衔接

Round 06：Review UI MVP
