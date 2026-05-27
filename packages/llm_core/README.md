# llm_core

## 模块职责

基于对齐结果与 ASR 时间戳，调用大模型生成结构化机切建议（`llm_cut_decision.json`）。

**重要边界：大模型只做文本层判断，不直接切音频。**

## 当前 Round 状态

**Round 00**：仅占位。**Round 05** 实现协议与 mock LLM。

## 未来要实现

- `MockLlmAdapter`
- `OpenAiCompatibleAdapter`（OpenAI / OpenRouter / 本地兼容端点）
- 输出 JSON 校验与 confidence 阈值过滤

## 输入 / 输出

- **输入**：alignment、transcript、normalized 文本
- **输出**：`llm_cut_decision.json`（action: keep/delete/uncertain）

## 与其他模块的关系

- 建议供前端 Review 页面展示
- 用户确认后汇总为 `cut_plan.json`
- 误判记录进入 `feedback_core`
