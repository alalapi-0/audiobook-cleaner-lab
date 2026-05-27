# 对齐策略（ALIGNMENT_STRATEGY）

## 目标

将 **normalized 原文** 与 **normalized ASR segments** 建立映射，识别匹配、多余、缺失、重复与不确定片段，供 LLM 与人工 Review 使用。

模块：`packages/alignment_core`（Round 04）。

## 对齐粒度

| 粒度 | 优点 | 缺点 | 本项目选择 |
|------|------|------|------------|
| 字符级 | 精细 | 中文 ASR 错字导致噪声大 | 辅助 similarity |
| 句子级 | 稳定 | 长句 ASR 切分不一 | **主路径** |
| 片段级（segment） | 与时间戳天然对齐 | 一段多句时复杂 | **与 ASR 对齐** |

**当前默认**：以 ASR segment 为单元，在原文中搜索最佳匹配窗口（滑动 + 相似度）。

## status 枚举

| status | 含义 | 后续处理 |
|--------|------|----------|
| `matched` | ASR 与原文高度一致 | 通常 keep |
| `extra_candidate` | ASR 有内容，原文无对应 | 疑似废话/口误/重读废弃 |
| `missing` | 原文有，ASR 无 | 漏读，一般不删音频 |
| `repeated` | 同一段原文多次 ASR | 保留最后一次 match，前序 delete 候选 |
| `uncertain` | 相似度中等 | 必须 LLM + 人工 |
| `low_similarity` | 相似度低于阈值 | 不自动 delete |

## 相似度

- 使用字符级或 token 级 ratio（如 SequenceMatcher）
- 阈值示例：matched ≥ 0.85，uncertain 0.5–0.85，low_similarity < 0.5
- 阈值可配置，feedback 可优化

## 输出结构

见 `DATA_MODEL.md` 中 `alignment.json`。每项含：

- `asr_segment_id`
- `source_range`（char 偏移，可为 null）
- `similarity`
- `status`

## 如何把 alignment 交给大模型

LLM 输入应包含（文本层）：

- 每个 segment 的 ASR 文本 + 时间戳
- 对应 source 文本片段（若有）
- `status` 与 `similarity`
- 前后 segment 上下文（各 1–2 段）

LLM **不接收**原始音频二进制；切点建议基于已有 `start`/`end` + padding。

## 如何避免误删正文

1. `matched` 默认 keep，LLM 不得仅因 filler 候选 delete
2. `low_similarity` 不自动 delete
3. `uncertain` 必须人工确认
4. delete 建议需 `reason_type` 与 `confidence`
5. 正文对话中的「嗯、啊」需结合 source 判断

## 重读与口误场景

典型模式：

```
seg_A: 读错的内容 (extra_candidate / low_similarity)
seg_B: 「不对，重新读」 (extra_candidate)
seg_C: 正确内容 (matched)
```

对齐器应标记 seg_A、seg_B 为 extra，LLM 建议 delete，用户 Review 确认。

## 风险

- 原文与口语朗读差异大 → 大量 uncertain
- 长章节性能 → Round 04 先 O(n) 贪心，后续优化
