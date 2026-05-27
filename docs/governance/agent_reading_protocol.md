# Agent 阅读协议

本文档说明后续 AI Agent 如何高效、安全地阅读本仓库。

## 每轮开始：固定入口（必读）

1. `README.md`
2. `AGENTS.md`
3. `PROJECT_STATE.md`
4. `docs/governance/repo_protocol_standard.yaml`
5. 当前 `rounds/round-XX-*.md`

## 按任务相关性扩展

| 任务类型 | 追加阅读 |
|----------|----------|
| 导入/Manifest | `DATA_MODEL.md` manifest 节、`round-01` |
| ASR | `ASR_STRATEGY.md`、`packages/asr_core/` |
| 文本清洗 | `TEXT_NORMALIZATION_RULES.md`、`packages/text_core/` |
| 对齐 | `ALIGNMENT_STRATEGY.md`、`packages/alignment_core/` |
| LLM 机切 | `LLM_CUT_DECISION_PROTOCOL.md`、`prompts/llm_cut_decision/` |
| Review UI | `UI_DESIGN.md`、`apps/web/` |
| 导出 | `AUDIO_EDITING_STRATEGY.md`、`packages/audio_core/` |
| 反馈 | `FEEDBACK_LOOP.md`、`packages/feedback_core/` |

## 如何避免全量读取

1. **禁止**递归 read 整个 `data/`、`packages/`、`docs/`
2. 用 `grep` 搜关键词（chapter_id、Adapter、cut_plan 等）
3. 用 `glob` 定位 `round-*.md`、`**/*.py`
4. 大文件先看标题与目录（Markdown `#` 行）
5. 二进制与音频**不读内容**，仅验证路径存在

## 如何判断当前任务相关文件

- 以当前 Round 文件的「主要任务」「输出文件」为准
- 以 `file_role_map.yaml` 的 module 映射为准
- 代码改动限定在 Round 声明的 packages/apps 内

## 更新 PROJECT_STATE

每轮结束更新：

- 当前 Stage / Round
- 已完成 / 未完成列表
- 下一轮目标
- 风险与默认假设
- 「最近更新记录」表格新增一行

## 更新 update_log

在 `docs/governance/update_log.md` 记录：

- 本轮创建/修改的文件
- 协议变更（若有）
- 留待后续 Round 的事项

## 记录协议变更

若修改 `repo_protocol_standard.yaml`：

1. 递增 `version` 或记录 patch 说明
2. 写入 `update_log.md`
3. 检查 `AGENTS.md` / `file_role_map.yaml` 是否需同步

## 禁止路径

勿扫描：`.git/`、`node_modules/`、`__pycache__/`、`.venv/`、`data/raw_audio/`、`data/exports/`、`logs/`

## 不确定时的行为

- 在代码或文档写 `TODO` + 默认假设
- 不擅自扩大 Round 范围
- 不调用真实 API
