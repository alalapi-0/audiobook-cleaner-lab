# alignment_core

## 模块职责

将清洗后的原文与 ASR 文本按片段对齐，识别 matched、extra、missing、repeated、uncertain 等状态。

## 当前 Round 状态

**Round 00**：仅占位。**Round 04** 实现基础 alignment 生成。

## 输入 / 输出

- **输入**：normalized 原文与 ASR 文本、transcript segments
- **输出**：`data/alignments/{chapter_id}.json`

## 与其他模块的关系

- 输出是 `llm_core` 机切建议的核心输入之一
- 对齐质量直接影响误删正文风险
