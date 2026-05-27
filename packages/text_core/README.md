# text_core

## 模块职责

分别清洗正确原文与 ASR 转写文本，统一标点、空格、全半角，并标记语气词/废话候选（不直接删除）。

## 当前 Round 状态

**Round 00**：仅占位。**Round 03** 实现最小 normalizer。

## 未来要实现

- `source_text_normalizer`
- `asr_text_normalizer`
- `filler_detector`（候选标记，非自动删除）

## 输入 / 输出

- **输入**：原始 TXT/MD 原文、ASR transcript
- **输出**：`normalized_source_text.json`、`normalized_asr_text.json`

## 与其他模块的关系

- 输出供 `alignment_core` 对齐
- 规则优化反馈来自 `feedback_core`
