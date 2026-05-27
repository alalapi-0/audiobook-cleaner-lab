# Round 04 — 原文与 ASR 对齐

**状态：已完成（2026-05-27）**

## Round 目标

生成 `alignment.json`，标注 matched / extra_candidate / missing / repeated / uncertain / low_similarity。

## 前置条件

Round 03 normalized 文本可用。

## 主要任务

- 实现 `packages/alignment_core` 基础对齐器
- 滑动窗口 + 相似度阈值
- 输出符合 `DATA_MODEL.md`

## 输出文件

- `packages/alignment_core/aligner.py`
- `data/alignments/` 本地产物

## 验收标准

- mock 章节生成合法 alignment.json
- status 枚举完整

## 不做什么

- 不调用 LLM

## 下一轮衔接

Round 05：LLM 机切建议
