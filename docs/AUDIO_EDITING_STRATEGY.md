# 音频剪辑策略（AUDIO_EDITING_STRATEGY）

## 非破坏式编辑

**原始音频永远只读。** 所有「删除」意图表达为 JSON 中的时间区间，最终通过 FFmpeg 生成新文件写入 `data/exports/`。

原因：

- 可反复调整 cut_plan 而不丢失素材
- 可对比导出前后时长与听感
- Git 不跟踪大体积二进制

## cut_plan 的作用

`cut_plan.json` 是**唯一权威**的导出输入，汇总：

- LLM 机切建议（经 Review 确认或修改）
- 用户波形拖动微调
- padding 调整

机切建议 (`llm_cut_decision.json`) ≠ 最终切点。

## delete_ranges 与 keep_ranges

| 结构 | 用途 |
|------|------|
| `delete_ranges` | 要从成片中移除的区间（口误、废话、重读废弃段） |
| `keep_ranges` | 可选；显式标记保留段，便于 UI 高亮与校验 |

导出逻辑：从原音频中**移除** `delete_ranges` 的并集（合并重叠区间后），保留其余部分。

每个 range 建议包含：

- `start` / `end`（秒，浮点）
- `reason` / `reason_type`
- `source_segment_ids`（追溯 ASR segment）
- `confirmed_by_user`（是否经人工确认）

## padding 策略

切点不宜紧贴 ASR segment 边界：

- **pre_padding**：删除区间开始前略扩展，避免残留辅音
- **post_padding**：删除区间结束后略扩展，避免截断字尾

默认值（当前假设）：pre 0.08s，post 0.12s，可在 Review 页与 feedback 中调整。

低置信度或 `uncertain` 建议**不自动应用 padding 删除**，必须人工试听。

## FFmpeg 导出策略

1. 读取 `cut_plan.json` 与原音频路径
2. 合并 `delete_ranges`
3. 生成 `filter_complex` 或使用 concat+trim 方案
4. 输出到 `export.output_path`

依赖本地安装 FFmpeg，Round 08 实现。

## dry-run 策略

正式导出前支持 dry-run：

- 输出将执行的 FFmpeg 命令
- 输出预计删除时长与区间列表
- **不写入**输出文件

用于验证 cut_plan 合理性。

## 为什么不直接覆盖原文件

- 误操作不可恢复
- 批处理多章时需保留对照
- 反馈闭环需对比 model 建议与最终切点

## 为什么机切不等于最终切点

1. ASR 时间戳有误差
2. LLM 可能误判
3. 听感需要人工 padding
4. `uncertain` 必须人工决策

流水线设计：**建议 → Review → cut_plan → 导出**。

## 与 LLM 的边界

大模型输出 `suggested_cut` 仅为建议区间；**不得**直接调用 FFmpeg 或修改音频文件。见 `LLM_CUT_DECISION_PROTOCOL.md`。
