# ASR 策略（ASR_STRATEGY）

## 设计原则

ASR 实现**可替换**，通过 Adapter 模式统一输出 `transcript.json`。Round 00 仅设计，Round 02 实现 mock。

## ASR Adapter 接口（草案）

```python
class AsrAdapter(Protocol):
    def transcribe(self, audio_path: str, chapter_id: str) -> dict:
        """返回符合 DATA_MODEL 的 transcript.json 结构。"""
```

## 支持的 Adapter（规划）

| Adapter | 阶段 | 说明 |
|---------|------|------|
| `MockAsrAdapter` | Round 02 | 返回固定或基于时长的 mock segments |
| `ImportTranscriptAdapter` | Round 02 | 读取用户提供的 transcript.json |
| `FasterWhisperAdapter` | 后续 | 本地 faster-whisper |
| `WhisperApiAdapter` | 后续 | OpenAI Whisper API |
| 其他云端 ASR | 后续 | 阿里云、讯飞等（需单独 Adapter） |

Round 00 **不接**真实 API。

## mock ASR

用于开发与测试：

- 不读取真实音频内容（可只读时长 metadata）
- 生成 3–5 个示例 segment
- `asr_engine: "mock"`

## 手动导入 transcript.json

用户若已有外部 ASR 结果：

- 放入 `data/transcripts/` 或通过 API 指定路径
- `ImportTranscriptAdapter` 校验 schema 后注册到 chapter_manifest

## 时间戳要求

### segment 级（Round 02 必须）

每个 segment 必须有：

- `segment_id`
- `start` / `end`（秒，浮点，end > start）
- `text`

### word / phrase 级（未来）

- 可选 `words[]` 子数组，含更细粒度时间戳
- 用于精确切点与波形对齐
- Round 02 不强制

## ASR 错误对后续的影响

| 错误类型 | 影响 | 缓解 |
|----------|------|------|
| 错字 | alignment similarity 下降 | LLM + 人工 |
| 时间戳漂移 | 切点偏早/偏晚 | padding + 波形微调 |
| 漏段 | missing alignment | 人工标记 keep |
| 多段合并 | 一对多对齐 | repeated / uncertain |

## 引擎元数据

transcript 应记录：

- `asr_engine`
- `created_at`
- 可选 `model_version`、`language`

## 当前默认假设

- 中文普通话有声书
- 单说话人
- segment 平均 3–15 秒
