# PROJECT_STATE.md — 项目当前状态

> 每轮完成后必须更新本文件。

## 当前 Stage

**Stage 12 — 连续自动推进与本地主链路巩固**

## 当前 Round

**Round 16 — Stitch Design MCP 集成与文档补全**（已完成）

**Round 15 — Playwright API Fixture**（已完成）

**Round 13 R2 — 真实 LLM API**（待用户配置 Key，非硬阻塞整体 mock 链路）

## 当前状态

`mock 主链路可一键验收` — `auto_advance.py` + `start_local.sh` 自动 seed 演示章节；Review API/UI 可在无 API Key 时端到端验证。

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
- [x] Round 12 — Agent MCP / agent_gate / 浏览器验证门禁
- [x] Round 13 R1 — 真实 LLM Adapter 骨架（无 Key 时跳过真实调用）
- [x] Round 14 — auto_advance、start_local 自动 seed、check_repo 扩展
- [x] Round 15 — Playwright 双 webServer + 波形按钮 ready 门禁
- [x] Round 16 — Stitch MCP（本地 proxy）、docs/design/、MCP/测试文档补全

## 下一轮目标

用户配置 `.env` 中 `LLM_API_KEY` 后完成 Round 13 R2（`real_api_check.py --pipeline`）

## 当前风险

| 风险 | 说明 | 缓解 |
|------|------|------|
| mock 与真实 ASR 差距 | 切点精度未知 | 接入真实 Adapter 后回归测试 |
| 前端未 CI 构建 | npm 依赖本地安装 | README + check_environment |
| 对齐算法简单 | 复杂口误场景 | LLM + 人工 Review |
| 无 API Key | 真实 LLM 未调用 | mock 链路 + Round 13 报告 exit 2 |

## 用户需要准备的内容

- 原始章节音频 + 原文文本（放 `data/`）
- Python 3.10+、FFmpeg、Node.js 18+
- 可选：ASR/LLM API Key（`.env`，不进 Git）

## 最近更新记录

| 日期 | Round | 摘要 |
|------|-------|------|
| 2026-06-06 | Round 16 | Stitch MCP、docs/design/stitch/、check:stitch、Agent 文档 |
| 2026-06-02 | Round 15 | Playwright API fixture、波形按钮 ready 门禁 |
| 2026-06-02 | Round 14 | auto_advance、start_local 自动 seed、agent:advance |
| 2026-06-01 | Round 13 R1 | OpenAiCompatibleAdapter、real_api_check（无 Key 硬阻塞真实调用） |
| 2026-06-01 | Round 12 | agent_gate、MCP/Skill/Rule、ManifestError→404、Review 初始 cut_plan UX |
| 2026-05-27 | Round 11 | check_environment、start_local.sh、README 教程 |
| 2026-05-27 | Round 10 | batch_process.py 多章节批处理 |
| 2026-05-27 | Round 09 | FeedbackService、feedback_record |
| 2026-05-27 | Round 08 | FfmpegExporter、run_export |
| 2026-05-27 | Round 07 | WaveformEditor、wavesurfer.js |
| 2026-05-27 | Round 06 | Review API + React MVP |
| 2026-05-27 | Round 01–05 | 核心 Python 流水线 |
| 2026-05-27 | Round 00 | 仓库初始化 |
