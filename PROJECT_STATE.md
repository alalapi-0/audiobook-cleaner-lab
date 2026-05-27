# PROJECT_STATE.md — 项目当前状态

> 每轮完成后必须更新本文件。

## 当前 Stage

**Stage 5 — 大模型机切建议**

## 当前 Round

**Round 05 — LLM 机切建议**（已完成，下一轮 Round 06）

## 当前状态

`LLM mock 可用` — MockLlmAdapter、LlmCutService、run_llm_cut CLI 已实现。

## 已完成内容

- [x] 单仓库目录结构（apps、packages、docs、rounds、prompts、scripts、tests）
- [x] 治理协议 `docs/governance/repo_protocol_standard.yaml`
- [x] 11 份设计文档 + 4 份治理文档
- [x] rounds/round-00 至 round-11 规划文件
- [x] `scripts/check_repo.py` 与 `scripts/init_data_dirs.py`
- [x] packages 六模块占位（audio/asr/text/alignment/llm/feedback）
- [x] `.gitignore` 排除 data 真实内容与音频大文件
- [x] manifest schema（`apps/api/schemas/manifest.py`）
- [x] ManifestService 与 `scripts/import_manifest.py` CLI
- [x] `tests/test_manifest_schema.py`（6 项测试）
- [x] MockAsrAdapter、ImportTranscriptAdapter、AsrService（Round 02）
- [x] `scripts/run_asr.py` CLI
- [x] `tests/test_asr_baseline.py`（3 项测试）
- [x] source/asr normalizer、filler_detector（Round 03）
- [x] `scripts/run_normalize.py` CLI
- [x] `tests/test_text_normalization.py`（7 项测试）
- [x] BaselineAligner、AlignmentService（Round 04）
- [x] `scripts/run_align.py` CLI
- [x] `tests/test_alignment.py`（3 项测试）
- [x] MockLlmAdapter、LlmCutService（Round 05）
- [x] `scripts/run_llm_cut.py` CLI
- [x] `tests/test_llm_cut_decision.py`（4 项测试）

## 未完成内容

- [x] 项目/章节导入与 manifest（Round 01）
- [x] ASR mock 与 transcript（Round 02）
- [x] 文本清洗 normalizer（Round 03）
- [x] 对齐 alignment（Round 04）
- [x] LLM 机切建议（Round 05）
- [ ] Review 网页 MVP（Round 06）
- [ ] 波形编辑器（Round 07）
- [ ] FFmpeg 导出（Round 08）
- [ ] 反馈闭环（Round 09）
- [ ] 批处理（Round 10）
- [ ] 本地一键启动（Round 11）

## 下一轮目标（Round 06）

Review UI MVP：Vite + React 三栏布局，保存 user_review 与 cut_plan。

## 当前风险

| 风险 | 说明 | 缓解 |
|------|------|------|
| ASR 时间戳不准 | 影响切点与对齐 | 人工 Review + padding 可调 |
| LLM 误删正文 | 高置信度自动删除风险 | uncertain 必须人工确认；低置信不自动删 |
| 对齐算法局限 | 重读/口误场景复杂 | 多 status 类型 + LLM + 人工 |
| 大文件 Git 误提交 | 音频进仓库 | .gitignore + check_repo 规则 |

## 当前默认假设

1. 中文有声书，个人本地单用户
2. Python 3.10+，FastAPI + React/Vite + SQLite + FFmpeg
3. ASR/LLM 通过 Adapter 可替换，Round 00–05 先用 mock
4. 非破坏式编辑，原音频只读
5. 不做云部署、不做多用户登录、不做模型微调（第一阶段）

## 用户需要准备的内容

- 原始章节音频（wav/mp3，放 `data/raw_audio/`）
- 对应正确原文文本（放 `data/source_text/`）
- 本地 FFmpeg（Round 08 起需要）
- 可选：ASR/LLM API Key（通过 `.env`，不进 Git）

## 最近更新记录

| 日期 | Round | 摘要 |
|------|-------|------|
| 2026-05-27 | Round 04 | BaselineAligner、AlignmentService、run_align CLI |
| 2026-05-27 | Round 03 | source/asr normalizer、filler_detector、run_normalize CLI |
| 2026-05-27 | Round 02 | MockAsrAdapter、ImportTranscriptAdapter、run_asr CLI |
| 2026-05-27 | Round 01 | manifest schema、ManifestService、import_manifest CLI、单元测试 |
| 2026-05-27 | Round 00 | 仓库初始化、治理协议、设计文档、检查脚本 |
