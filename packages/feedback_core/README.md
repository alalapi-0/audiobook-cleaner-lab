# feedback_core

## 模块职责

比较模型机切建议与用户最终 cut plan 的差异，生成统计报告与规则/prompt/padding 优化建议。

## 当前 Round 状态

**Round 00**：仅占位。**Round 09** 实现 feedback_record 与基础统计。

## 输入 / 输出

- **输入**：`llm_cut_decision.json`、`user_review.json`、最终 `cut_plan.json`
- **输出**：`feedback_record.json`、章节/全书统计报告

## 与其他模块的关系

- 反馈优化 `text_core` 规则与 `llm_core` prompt
- 反馈优化 `audio_core` padding 默认值

## 当前默认假设

第一阶段不做模型微调，仅优化规则与 prompt。
