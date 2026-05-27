# Round 10 — 批处理

**状态：已完成（2026-05-27）**

## Round 目标

整本书多章节队列处理、状态管理、失败重试。

## 前置条件

Round 02–09 单章流程可跑通（mock 亦可）。

## 主要任务

- 章节队列 CLI
- status 流转：imported → asr_done → … → exported
- 失败重试与日志

## 输出文件

- `scripts/batch_process.py` 或 API 批处理端点
- 更新 `project_manifest.chapters[].status`

## 验收标准

- mock 3 章顺序执行并更新状态

## 不做什么

- 不做分布式任务队列

## 完成记录

- [x] `scripts/batch_process.py` — 顺序执行 ASR→normalize→align→llm→auto_review→export dry-run→feedback

## 下一轮衔接

Round 11：本地一键启动
