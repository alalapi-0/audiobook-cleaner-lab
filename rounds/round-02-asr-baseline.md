# Round 02 — ASR 基线

**状态：已完成（2026-05-27）**

## Round 目标

输入章节音频路径，输出带 segment 时间戳的 `transcript.json`（mock 或手动导入）。

## 前置条件

Round 01 manifest 可用。

## 主要任务

- 实现 `MockAsrAdapter`、`ImportTranscriptAdapter`
- 统一 `AsrAdapter` 接口
- CLI/API：`run-asr --chapter-id`

## 输出文件

- `packages/asr_core/adapters/`（mock、import）
- 更新 `chapter_manifest.artifacts.transcript`

## 验收标准

- mock 生成合法 transcript.json
- 手动导入路径校验通过
- segment 含 start/end/text

## 不做什么

- 不接真实 Whisper API（可留接口）

## 完成记录

- [x] `packages/asr_core/base.py` — AsrAdapter 接口
- [x] `packages/asr_core/adapters/mock.py` — MockAsrAdapter
- [x] `packages/asr_core/adapters/import_adapter.py` — ImportTranscriptAdapter
- [x] `packages/asr_core/service.py` — AsrService，更新 chapter manifest
- [x] `scripts/run_asr.py` — CLI
- [x] `tests/test_asr_baseline.py` — 3 项测试

## 验收结果

```bash
python3 scripts/check_repo.py
python3 -m unittest tests.test_asr_baseline -v  # 3 tests OK
```

## 下一轮衔接

Round 03：文本正则清洗
