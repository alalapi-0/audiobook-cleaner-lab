# Round 08 — FFmpeg 非破坏式导出

## Round 目标

根据 `cut_plan.json` dry-run 与正式导出干净音频，生成 `export_report.json`。

## 前置条件

Round 07 cut_plan 可编辑；本地安装 FFmpeg。

## 主要任务

- `packages/audio_core/ffmpeg_exporter.py`
- dry-run 输出命令与统计
- 正式导出到 `data/exports/`
- **不覆盖原音频**

## 输出文件

- export API/CLI
- `export_report.json`

## 验收标准

- dry-run 命令正确
- 正式导出时长符合 delete_ranges

## 不做什么

- 不批处理多章（Round 10）

## 下一轮衔接

Round 09：反馈闭环
