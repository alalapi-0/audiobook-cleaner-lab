# 流水线设计（PIPELINE_DESIGN）

本文档描述从原始素材到干净音频的完整处理链。每一步标明输入、输出、负责模块、当前 Round 实现状态与风险。

## 总览

```
[导入] → [预处理] → [ASR] → [文本清洗] → [对齐]
    → [LLM 机切] → [人工 Review] → [cut_plan] → [FFmpeg 导出] → [反馈]
```

---

## 1. 导入音频与原文

| 项 | 说明 |
|----|------|
| **输入** | 用户指定的 WAV/MP3 路径、TXT/MD 原文路径 |
| **输出** | `project_manifest.json`、`chapter_manifest.json` |
| **模块** | `apps/api`（Round 01） |
| **Round** | Round 01 实现 |
| **风险** | 路径错误、章节与音频不匹配 |

## 2. 音频预处理

| 项 | 说明 |
|----|------|
| **输入** | 原始音频 |
| **输出** | 预处理报告（采样率、声道、时长、建议参数） |
| **模块** | `packages/audio_core` |
| **Round** | Round 02+ 逐步引入 |
| **风险** | 格式异常、过长静音 |

## 3. ASR 识别

| 项 | 说明 |
|----|------|
| **输入** | 章节音频 |
| **输出** | `transcript.json`（segment 级时间戳） |
| **模块** | `packages/asr_core` |
| **Round** | Round 02 mock / 手动导入 |
| **风险** | 识别错误影响对齐；时间戳边界不准 |

## 4. 原文正则清洗

| 项 | 说明 |
|----|------|
| **输入** | 原始原文 |
| **输出** | `normalized_source_text.json` |
| **模块** | `packages/text_core` |
| **Round** | Round 03 |
| **风险** | 过度规范化丢失语义 |

## 5. ASR 正则清洗

| 项 | 说明 |
|----|------|
| **输入** | `transcript.json` |
| **输出** | `normalized_asr_text.json` |
| **模块** | `packages/text_core` |
| **风险** | 误删 ASR 中有意义的语气词 |

## 6. 文本对齐

| 项 | 说明 |
|----|------|
| **输入** | normalized 原文 + ASR |
| **输出** | `alignment.json` |
| **模块** | `packages/alignment_core` |
| **Round** | Round 04 |
| **风险** | 重读/口误导致多对一或一对多 |

## 7. 大模型判断（文本层）

| 项 | 说明 |
|----|------|
| **输入** | alignment、transcript、normalized 文本 |
| **输出** | `llm_cut_decision.json` |
| **模块** | `packages/llm_core` |
| **Round** | Round 05 |
| **风险** | 误判正文；**不直接切音频** |

## 8. 生成机切建议

机切建议 = LLM 输出的 `action` + `suggested_cut`（基于 ASR 时间戳 + padding）。仍为建议，非最终切点。

## 9. 人工校正

| 项 | 说明 |
|----|------|
| **输入** | 机切建议、alignment、音频 |
| **输出** | `user_review.json`、修订后的 `cut_plan.json` |
| **模块** | `apps/web` |
| **Round** | Round 06–07 |
| **风险** | UX 复杂导致校正效率低 |

## 10. 保存 cut plan

| 项 | 说明 |
|----|------|
| **输入** | 用户确认的删除/保留区间 |
| **输出** | `cut_plan.json` |
| **模块** | `apps/api` + `apps/web` |
| **Round** | Round 06+ |
| **风险** | 区间重叠或遗漏 |

## 11. FFmpeg 导出

| 项 | 说明 |
|----|------|
| **输入** | 原音频（只读）+ `cut_plan.json` |
| **输出** | 干净音频 + `export_report.json` |
| **模块** | `packages/audio_core` |
| **Round** | Round 08 |
| **风险** | padding 不足产生爆音/断句 |

## 12. 反馈优化

| 项 | 说明 |
|----|------|
| **输入** | model decision vs user final |
| **输出** | `feedback_record.json`、统计报告 |
| **模块** | `packages/feedback_core` |
| **Round** | Round 09 |
| **风险** | 样本不足时优化建议不可靠 |

---

## 非破坏式原则（贯穿全流程）

- 原始音频永不覆盖
- 所有剪辑意图存 JSON
- 导出写入 `data/exports/`

## 当前默认假设

- 按章节为单位处理，全书批处理在 Round 10
- SQLite 存项目元数据（Round 01 起设计）
