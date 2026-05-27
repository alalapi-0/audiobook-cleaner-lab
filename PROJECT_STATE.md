# PROJECT_STATE.md — 项目当前状态

> 每轮完成后必须更新本文件。

## 当前 Stage

**Stage 11 — 本地运行与使用体验（全部 Stage 0–11 已完成）**

## 当前 Round

**Round 11 — 本地一键启动**（已完成）

## 当前状态

`端到端 mock 流水线可运行` — Round 00–11 全部完成。用户可导入素材、跑 mock ASR/LLM、Web Review、波形微调、FFmpeg 导出与反馈分析。

## 已完成内容

- [x] Round 00 — 仓库骨架与治理
- [x] Round 01 — manifest 导入
- [x] Round 02 — ASR mock
- [x] Round 03 — 文本清洗
- [x] Round 04 — 对齐
- [x] Round 05 — LLM mock 机切
- [x] Round 06 — Review UI MVP
- [x] Round 07 — 波形编辑器
- [x] Round 08 — FFmpeg 导出
- [x] Round 09 — 反馈闭环
- [x] Round 10 — 批处理
- [x] Round 11 — 环境检查与一键启动

## 下一轮目标

进入维护迭代。新需求开 Stage 12+ 或新 Round：
- 真实 ASR Adapter（Whisper / faster-whisper）
- 真实 LLM Adapter（OpenAI 兼容 API）
- SQLite 持久化
- docker-compose

## 当前风险

| 风险 | 说明 | 缓解 |
|------|------|------|
| mock 与真实 ASR 差距 | 切点精度未知 | 接入真实 Adapter 后回归测试 |
| 前端未 CI 构建 | npm 依赖本地安装 | README + check_environment |
| 对齐算法简单 | 复杂口误场景 | LLM + 人工 Review |

## 用户需要准备的内容

- 原始章节音频 + 原文文本（放 `data/`）
- Python 3.10+、FFmpeg、Node.js 18+
- 可选：ASR/LLM API Key（`.env`，不进 Git）

## 最近更新记录

| 日期 | Round | 摘要 |
|------|-------|------|
| 2026-05-27 | Round 11 | check_environment、start_local.sh、README 教程 |
| 2026-05-27 | Round 10 | batch_process.py 多章节批处理 |
| 2026-05-27 | Round 09 | FeedbackService、feedback_record |
| 2026-05-27 | Round 08 | FfmpegExporter、run_export |
| 2026-05-27 | Round 07 | WaveformEditor、wavesurfer.js |
| 2026-05-27 | Round 06 | Review API + React MVP |
| 2026-05-27 | Round 01–05 | 核心 Python 流水线 |
| 2026-05-27 | Round 00 | 仓库初始化 |
