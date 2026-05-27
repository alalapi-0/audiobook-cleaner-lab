# 大模型机切决策协议（LLM_CUT_DECISION_PROTOCOL）

## 核心原则

> **大模型只做文本层判断，不直接切音频。**

大模型**不得**：

- 调用 FFmpeg 或任何音频处理工具
- 直接修改、覆盖、删除音频文件
- 凭空改写原文内容
- 在没有 ASR 时间戳的情况下编造切点

大模型**应当**：

- 基于 alignment、transcript、normalized 文本做语义判断
- 输出结构化 JSON（`llm_cut_decision.json`）
- 为 delete 建议提供基于 **已有 segment 时间戳** 的 `suggested_cut`
- 对低置信度输出 `uncertain`

---

## 大模型的职责

| 判断项 | 说明 |
|--------|------|
| 正文归属 | 哪些 ASR 片段属于原文 |
| 废话候选 | 哪些片段疑似 off-script |
| 废弃重读 | 读错后放弃的版本 |
| 重新开始 | 重读前的错误内容 |
| 原文不匹配 | 与 source 明显不符 |
| 人工确认 | 哪些必须人听 |

---

## 输入格式（草案）

```json
{
  "chapter_id": "chapter_001",
  "source_excerpt": "……正确原文摘要或全文……",
  "segments": [
    {
      "segment_id": "seg_0002",
      "start": 4.82,
      "end": 8.15,
      "asr_text": "嗯不对我重新读",
      "alignment_status": "extra_candidate",
      "similarity": 0.15,
      "context_before": "seg_0001 文本",
      "context_after": "seg_0003 文本"
    }
  ],
  "policy": {
    "never_auto_delete_below_confidence": 0.75,
    "require_user_for_uncertain": true
  }
}
```

Prompt 模板存放：`prompts/llm_cut_decision/`（Round 05 填充）。

---

## 输出格式

**必须是 JSON**，符合 `llm_cut_decision.json` schema。

### action 枚举

| action | 含义 |
|--------|------|
| `keep` | 保留该 segment 对应音频 |
| `delete` | 建议删除（仍需 Review，高置信度可预填 cut_plan） |
| `uncertain` | 无法自动决策，**必须人工确认** |

### reason_type 枚举（示例）

| reason_type | 含义 |
|-------------|------|
| `matches_source` | 与原文匹配 |
| `restart_phrase` | 重读前废弃内容 |
| `off_script` | 偏离原文的废话/说明 |
| `filler` | 语气词/填充词（非正文） |
| `misread` | 读错且已被后续正确版本替代 |
| `ambiguous_filler` | 可能是 filler 也可能是正文 |
| `low_confidence` | 模型不确定 |

### 字段说明

| 字段 | 说明 |
|------|------|
| `confidence` | 0.0–1.0 |
| `suggested_cut` | `{ start, end, pre_padding, post_padding }`，基于 segment 时间戳 |
| `reason` | 人类可读中文说明 |

---

## 安全规则

1. **low confidence 不得自动删除**：`confidence < 0.75` 时 action 应为 `uncertain` 或 `keep`，不得单独 `delete` 并自动进 cut_plan
2. **uncertain 必须人工确认**：UI 强制 Review
3. **不允许模型凭空改写原文**：reason 不得声称 source 中有不存在的内容
4. **不允许误判正文为废话**：对 `matched` + 高 similarity 的 segment，默认 `keep`
5. **切点来源**：`suggested_cut.start/end` 必须来自输入 segment 的 `start/end` ± padding，不得 hallucinate 新时间

---

## 示例输出 JSON

```json
{
  "chapter_id": "chapter_001",
  "llm_engine": "mock",
  "decisions": [
    {
      "segment_id": "seg_0001",
      "action": "keep",
      "reason_type": "matches_source",
      "reason": "与原文一致，保留",
      "suggested_cut": null,
      "confidence": 0.96
    },
    {
      "segment_id": "seg_0002",
      "action": "delete",
      "reason_type": "restart_phrase",
      "reason": "该片段是重读前的废弃内容，不属于原文",
      "suggested_cut": {
        "start": 4.82,
        "end": 8.15,
        "pre_padding": 0.08,
        "post_padding": 0.12
      },
      "confidence": 0.87
    },
    {
      "segment_id": "seg_0003",
      "action": "uncertain",
      "reason_type": "ambiguous_filler",
      "reason": "「嗯」可能是语气词或正文开头，需人工试听",
      "suggested_cut": {
        "start": 8.15,
        "end": 9.0,
        "pre_padding": 0.05,
        "post_padding": 0.05
      },
      "confidence": 0.52
    }
  ]
}
```

---

## 与 cut_plan 的关系

```
llm_cut_decision.json  →  Review UI  →  user_review.json  →  cut_plan.json  →  FFmpeg
     （建议）              （确认）         （记录）            （权威）          （执行）
```

LLM 输出停留在「建议」层；**唯一执行层**是 FFmpeg 读取 `cut_plan.json`。

---

## Adapter

`packages/llm_core` 提供：

- `MockLlmAdapter`（Round 05）
- `OpenAiCompatibleAdapter`（后续，Key 来自 `.env`）

Round 00 不接真实 API。
