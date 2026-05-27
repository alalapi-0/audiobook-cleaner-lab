# PROJECT_STATE.md — 项目当前状态

> 每轮完成后必须更新本文件。

## 当前 Stage

**Stage 8 — FFmpeg 非破坏式导出**

## 当前 Round

**Round 08 — FFmpeg 导出**（已完成，下一轮 Round 09）

## 当前状态

`端到端流水线 MVP 可用` — Round 01–08 已实现：导入 → ASR mock → 清洗 → 对齐 → LLM mock → Review UI → 波形 → FFmpeg 导出。

## 已完成内容

- [x] Round 01 — manifest schema、ManifestService、import_manifest CLI
- [x] Round 02 — MockAsrAdapter、ImportTranscriptAdapter、run_asr CLI
- [x] Round 03 — source/asr normalizer、filler_detector、run_normalize CLI
- [x] Round 04 — BaselineAligner、AlignmentService、run_align CLI
- [x] Round 05 — MockLlmAdapter、LlmCutService、run_llm_cut CLI
- [x] Round 06 — ReviewService、FastAPI、React Review 三栏 MVP
- [x] Round 07 — WaveformEditor（wavesurfer.js）、cut-plan 微调 API
- [x] Round 08 — FfmpegExporter、ExportService、run_export CLI

## 未完成内容

- [ ] 反馈闭环（Round 09）
- [ ] 批处理（Round 10）
- [ ] 本地一键启动（Round 11）

## 下一轮目标（Round 09）

实现 feedback_record 收集与规则优化建议。

## 当前风险

| 风险 | 说明 | 缓解 |
|------|------|------|
| ASR 时间戳不准 | 影响切点与对齐 | 人工 Review + padding 可调 |
| LLM 误删正文 | 高置信度自动删除风险 | uncertain 必须人工确认；低置信不自动删 |
| 对齐算法局限 | 重读/口误场景复杂 | 多 status 类型 + LLM + 人工 |
| 大文件 Git 误提交 | 音频进仓库 | .gitignore + check_repo 规则 |
| 前端需 npm install | Round 06+ 前端依赖 | 文档说明 `cd apps/web && npm install` |

## 当前默认假设

1. 中文有声书，个人本地单用户
2. Python 3.10+，FastAPI + React/Vite + FFmpeg
3. ASR/LLM 通过 Adapter 可替换，当前使用 mock
4. 非破坏式编辑，原音频只读
5. 本地 FFmpeg 已安装（macOS Homebrew）

## 用户需要准备的内容

- 原始章节音频（wav/mp3，放 `data/raw_audio/`）
- 对应正确原文文本（放 `data/source_text/`）
- 本地 FFmpeg（Round 08 起需要）
- Node.js 18+（Round 06 前端）
- 可选：ASR/LLM API Key（通过 `.env`，不进 Git）

## 最近更新记录

| 日期 | Round | 摘要 |
|------|-------|------|
| 2026-05-27 | Round 08 | FfmpegExporter、ExportService、run_export CLI |
| 2026-05-27 | Round 07 | WaveformEditor、cut-plan API、音频只读路由 |
| 2026-05-27 | Round 06 | Review API、React Review MVP、user_review/cut_plan |
| 2026-05-27 | Round 05 | MockLlmAdapter、LlmCutService、run_llm_cut CLI |
| 2026-05-27 | Round 04 | BaselineAligner、AlignmentService、run_align CLI |
| 2026-05-27 | Round 03 | source/asr normalizer、filler_detector |
| 2026-05-27 | Round 02 | MockAsrAdapter、ImportTranscriptAdapter |
| 2026-05-27 | Round 01 | manifest schema、ManifestService |
| 2026-05-27 | Round 00 | 仓库初始化 |
