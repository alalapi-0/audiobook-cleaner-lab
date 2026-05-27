# 阶段路线图（STAGE_ROADMAP）

Stage 0–11 与 Round 00–11 一一对应。每阶段含目标、Round、产物、验收标准与不做什么。

---

## Stage 0 — 仓库治理与项目骨架

**对应 Round**：Round 00

**阶段目标**：建立单仓库骨架、治理协议、路线图、数据模型、检查脚本。

**主要产物**：

- 完整目录结构
- 设计文档与治理文档
- `scripts/check_repo.py`、`scripts/init_data_dirs.py`

**验收标准**：

```bash
python scripts/check_repo.py
python scripts/init_data_dirs.py
python scripts/check_repo.py
```

**不做什么**：不实现 ASR/LLM/前端/FFmpeg。

---

## Stage 1 — 素材导入与项目 Manifest

**对应 Round**：Round 01

**阶段目标**：创建书籍项目、章节、导入路径，生成 manifest。

**主要产物**：`project_manifest.json`、`chapter_manifest.json`、导入 CLI/API 占位

**验收标准**：可创建示例 manifest 并通过 schema 校验脚本

**不做什么**：不跑 ASR、不读真实大文件内容进 Git

---

## Stage 2 — ASR 识别与 transcript.json

**对应 Round**：Round 02

**阶段目标**：输入音频路径，输出带时间戳 transcript。

**主要产物**：`MockAsrAdapter`、`ImportTranscriptAdapter`、`transcript.json`

**验收标准**：mock 生成 transcript；手动导入路径可用

**不做什么**：不接真实 Whisper API（可留 Adapter 接口）

---

## Stage 3 — 文本正则清洗

**对应 Round**：Round 03

**阶段目标**：清洗原文与 ASR 文本。

**主要产物**：`source_text_normalizer`、`asr_text_normalizer`、`filler_detector`（候选）

**验收标准**：示例文本输入输出符合 `TEXT_NORMALIZATION_RULES.md`

**不做什么**：不自动删除语气词，仅标记候选

---

## Stage 4 — 原文与 ASR 对齐

**对应 Round**：Round 04

**阶段目标**：生成 `alignment.json`，标注 matched/extra/missing 等。

**主要产物**：`alignment_core` 基础对齐器

**验收标准**：mock 数据生成合法 alignment.json

**不做什么**：不追求完美对齐，先覆盖主路径

---

## Stage 5 — 大模型机切建议

**对应 Round**：Round 05

**阶段目标**：LLM 输出结构化机切建议 JSON。

**主要产物**：`LLM_CUT_DECISION_PROTOCOL` 实现、`MockLlmAdapter`

**验收标准**：mock LLM 输出通过 schema；明确不直接切音频

**不做什么**：不接真实付费 API；不自动执行删除

---

## Stage 6 — 人工校正页面 MVP

**对应 Round**：Round 06

**阶段目标**：网页查看原文/ASR/建议并确认驳回。

**主要产物**：Review 页面 MVP、`user_review.json` 保存

**验收标准**：本地可打开页面并完成 mock 章节 Review 流程

**不做什么**：不做完整波形编辑（Stage 7）

---

## Stage 7 — 波形时间轴编辑器

**对应 Round**：Round 07

**阶段目标**：wavesurfer.js 可视化切点拖动。

**主要产物**：波形组件、切点拖动、区间高亮

**验收标准**：可拖动调整切点并写回 cut_plan

**不做什么**：不做多轨混音

---

## Stage 8 — FFmpeg 非破坏式导出

**对应 Round**：Round 08

**阶段目标**：按 cut_plan 导出干净音频。

**主要产物**：dry-run + 正式导出、`export_report.json`

**验收标准**：mock cut_plan 生成正确 FFmpeg 命令；本地 FFmpeg 可导出

**不做什么**：不覆盖原文件

---

## Stage 9 — 反馈优化闭环

**对应 Round**：Round 09

**阶段目标**：记录 model vs user 差异，输出优化建议。

**主要产物**：`feedback_record.json`、统计报告

**验收标准**：示例 diff 生成 lesson 字段

**不做什么**：不做模型微调

---

## Stage 10 — 批处理

**对应 Round**：Round 10

**阶段目标**：多章节队列、状态、失败重试。

**主要产物**：章节队列管理、批处理 CLI

**验收标准**：mock 多章顺序执行并更新状态

**不做什么**：不做分布式任务系统

---

## Stage 11 — 本地运行与使用体验

**对应 Round**：Round 11

**阶段目标**：一键启动、检查脚本、README 教程。

**主要产物**：`scripts/start_local.sh`、完整使用文档

**验收标准**：新用户按 README 可完成单章 mock 全流程

**不做什么**：不做云部署与安装包分发

---

## Round 索引

| Round | 名称 | 文件 |
|-------|------|------|
| 00 | 仓库初始化 | `rounds/round-00-bootstrap.md` |
| 01 | 导入 Manifest | `rounds/round-01-import-manifest.md` |
| 02 | ASR 基线 | `rounds/round-02-asr-baseline.md` |
| 03 | 文本清洗 | `rounds/round-03-text-normalization.md` |
| 04 | 对齐 | `rounds/round-04-alignment.md` |
| 05 | LLM 机切 | `rounds/round-05-llm-cut-decision.md` |
| 06 | Review UI | `rounds/round-06-review-ui-mvp.md` |
| 07 | 波形编辑 | `rounds/round-07-waveform-editor.md` |
| 08 | FFmpeg 导出 | `rounds/round-08-ffmpeg-export.md` |
| 09 | 反馈闭环 | `rounds/round-09-feedback-loop.md` |
| 10 | 批处理 | `rounds/round-10-batch-processing.md` |
| 11 | 本地启动 | `rounds/round-11-local-runner.md` |
