# asr_core

## 模块职责

提供可替换的 ASR Adapter，将原始音频转为带时间戳的 `transcript.json`。

## 当前 Round 状态

**Round 00**：仅占位。**Round 02** 实现 mock ASR 与手动导入。

## 未来要实现

- `MockAsrAdapter`：返回固定示例 segment
- `ImportTranscriptAdapter`：读取用户提供的 transcript.json
- `FasterWhisperAdapter`（后续）
- `WhisperApiAdapter`（后续）

## 输入 / 输出

- **输入**：章节音频路径、`chapter_id`
- **输出**：`data/transcripts/{chapter_id}.json`

## 与其他模块的关系

- 输出供 `text_core` 做 ASR 文本清洗
- 输出供 `alignment_core` 与原文对齐
- segment 时间戳是后续切点的权威来源之一
