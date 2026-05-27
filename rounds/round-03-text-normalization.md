# Round 03 — 文本正则清洗

**状态：已完成（2026-05-27）**

## Round 目标

实现 `source_text_normalizer`、`asr_text_normalizer`、`filler_detector`（候选标记）。

## 前置条件

Round 02 transcript 可用；章节原文路径已登记。

## 主要任务

- 按 `TEXT_NORMALIZATION_RULES.md` 实现规则
- 输出 `normalized_source_text.json`、`normalized_asr_text.json`
- filler 仅标记 `auto_delete: false`

## 输出文件

- `packages/text_core/normalizers.py`
- 配置示例 `config/text_normalization.example.yaml`

## 验收标准

- 示例文本输入输出符合文档
- 不粗暴删除语气词

## 不做什么

- 不做 alignment

## 完成记录

- [x] `packages/text_core/normalizers.py`
- [x] `packages/text_core/filler_detector.py`
- [x] `packages/text_core/service.py`
- [x] `config/text_normalization.example.yaml`
- [x] `scripts/run_normalize.py`
- [x] `tests/test_text_normalization.py` — 7 项测试

## 验收结果

```bash
python3 -m unittest tests.test_text_normalization -v  # 7 tests OK
```

## 下一轮衔接

Round 04：alignment.json
