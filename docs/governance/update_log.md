# 治理协议更新日志

## Round 05 — 2026-05-27 — 大模型机切建议

### 新增代码

- `packages/llm_core/` — MockLlmAdapter、LlmCutService
- `prompts/llm_cut_decision/system_mock.md`
- `scripts/run_llm_cut.py`
- `tests/test_llm_cut_decision.py`

---

## Round 04 — 2026-05-27 — 原文与 ASR 对齐

### 新增代码

- `packages/alignment_core/` — BaselineAligner、AlignmentService
- `scripts/run_align.py`
- `tests/test_alignment.py`

---

## Round 03 — 2026-05-27 — 文本正则清洗

### 新增代码

- `packages/text_core/` — normalizers、filler_detector、service
- `config/text_normalization.example.yaml`
- `scripts/run_normalize.py`
- `tests/test_text_normalization.py`

---

## Round 02 — 2026-05-27 — ASR 基线

### 新增代码

- `packages/asr_core/` — AsrAdapter、MockAsrAdapter、ImportTranscriptAdapter、AsrService
- `scripts/run_asr.py` — ASR CLI
- `tests/test_asr_baseline.py`

---

## Round 01 — 2026-05-27 — 素材导入与 Manifest

### 新增代码

- `apps/api/schemas/manifest.py` — manifest dataclass schema
- `apps/api/services/manifest_service.py` — 项目/章节 CRUD 与路径校验
- `scripts/import_manifest.py` — CLI 导入工具
- `tests/test_manifest_schema.py` — schema 与服务单元测试

### 变更

- `scripts/init_data_dirs.py` — 新增 `data/projects/` 子目录
- `PROJECT_STATE.md` — Stage 1 / Round 01 完成

### 默认假设

- manifest 存于 `data/projects/{project_id}/`
- 章节 manifest 存于 `data/projects/{project_id}/chapters/{chapter_id}/`
- 使用 stdlib dataclass，Round 02 前不引入 Pydantic 依赖

---

## Round 00 — 2026-05-27 — 仓库初始化

### 创建了哪些目录

- `apps/api/`（routes、services）
- `apps/web/`（src、public）
- `packages/`（audio_core、asr_core、text_core、alignment_core、llm_core、feedback_core）
- `docs/` + `docs/governance/`
- `rounds/`、`prompts/`（system、round_prompts、llm_cut_decision）
- `scripts/`、`tests/`、`data/`

### 创建了哪些文档

**根目录**：README.md、AGENTS.md、PROJECT_STATE.md

**设计文档（11）**：

- PROJECT_VISION.md、PIPELINE_DESIGN.md、STAGE_ROADMAP.md、DATA_MODEL.md
- AUDIO_EDITING_STRATEGY.md、TEXT_NORMALIZATION_RULES.md、ASR_STRATEGY.md
- ALIGNMENT_STRATEGY.md、LLM_CUT_DECISION_PROTOCOL.md、UI_DESIGN.md、FEEDBACK_LOOP.md

**治理文档（4）**：

- repo_protocol_standard.yaml、file_role_map.yaml、agent_reading_protocol.md、update_log.md（本文件）

**Round 文件（12）**：round-00 至 round-11

### 从既有协议文件吸收的规则

参考：`novel-continuation-agent/governance/repo_protocol_standard.yaml` v0.2.2

| 吸收项 | 本项目应用 |
|--------|------------|
| Agent 先读治理再读代码 | AGENTS.md + agent_reading_protocol.md |
| search_first_policy | 禁止全量读 data/ |
| forbidden_scan_paths | 写入 repo_protocol_standard.yaml |
| file_role_taxonomy | 适配为 file_role_map.yaml |
| round 生命周期 | rounds/ + PROJECT_STATE 更新规则 |
| secret_policy | 禁止 .env 进 Git |
| document vs yaml 职责 | 状态在 PROJECT_STATE，协议在 yaml |
| sync_requirements | 每轮更新 state + update_log |
| 非破坏式与 archive 思想 | 音频只读 + JSON 切点 |

### 为本项目新增的规则

| 规则 | 说明 |
|------|------|
| llm_boundary | LLM 不直接切音频 |
| data/** gitignore | 大文件隔离 |
| non_destructive_edit | cut_plan 为导出权威 |
| ASR/LLM Adapter | 可替换，Round 02/05 mock |
| 11 种 JSON schema | DATA_MODEL.md |
| check_repo.py | Round 00 验收 |

### 留待后续 Round

- 业务代码（ASR、对齐、LLM、UI、FFmpeg）
- FastAPI 真实路由与 SQLite
- React 前端与 wavesurfer.js
- prompt 模板内容
- 单元测试

### 协议版本

- `repo_protocol_standard.yaml` version: **1.0.0**
