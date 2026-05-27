# audiobook-cleaner-lab

**个人有声书音频清洗与文本对齐剪辑工具**

## 项目说明

本项目用于将个人录制的中文有声书原始录音，结合正确原文文本，通过 ASR、文本对齐、大模型机切建议与人工校正，最终导出干净、连续、可发布的有声书音频。

这不是通用 DAW 剪辑软件，而是一条 **原文 + ASR + LLM + 人工 Review + FFmpeg** 的专用流水线。

## 适用场景

- 自录有声书，录音中包含口误、重读、废话、试读、停顿等需删除内容
- 已有与音频对应的正确原文文本
- 希望半自动机切 + 网页人工校正，而非纯手工波形剪辑
- 个人本地使用，非多用户 SaaS

## 输入与输出

| 类型 | 内容 |
|------|------|
| **输入** | 原始音频、对应原文文本 |
| **中间产物** | transcript、alignment、llm_cut_decision、cut_plan、user_review |
| **输出** | 干净版音频、cut_plan.json、export_report.json、feedback_record |

## 总体流水线

```
导入音频/原文 → 音频预处理 → ASR → 文本清洗 → 对齐
    → LLM 机切建议 → 人工校正 → cut_plan → FFmpeg 导出 → 反馈优化
```

**重要**：大模型只做文本层判断，**不直接切音频**。切点来自 ASR 时间戳、对齐结果与用户人工调整。

## 当前状态

- **Stage 1 — 素材导入与项目 Manifest**
- **Round 01 — 素材导入与 Manifest**（已完成）
- 已实现 manifest schema、ManifestService 与 `scripts/import_manifest.py` CLI

后续按 `rounds/` 目录逐轮推进（当前 Round 02 — ASR 基线）。

## 大文件与 Git 策略

- 真实音频、导出音频、ASR/对齐/cut plan 等中间产物默认放在 `data/` 目录
- **`data/` 真实内容不进入 Git**，仅保留 `.gitkeep`
- 音频扩展名（wav/mp3/m4a 等）已在 `.gitignore` 中排除

## 本轮验收

```bash
cd audiobook-cleaner-lab
python scripts/check_repo.py
python scripts/init_data_dirs.py
python scripts/check_repo.py
```

两次 `check_repo.py` 均应输出「仓库骨架检查通过」。

## 素材导入（Round 01）

```bash
python3 scripts/import_manifest.py create-project --project-id book_001 --title "示例有声书"
python3 scripts/import_manifest.py add-chapter \
  --project-id book_001 --chapter-id chapter_001 --title "第一章" \
  --audio data/raw_audio/book_001/chapter_001.wav \
  --text data/source_text/book_001/chapter_001.txt
```

详见 `rounds/round-01-import-manifest.md`。

## 快速导航

| 文档 | 用途 |
|------|------|
| [AGENTS.md](AGENTS.md) | AI Agent 工作规范 |
| [PROJECT_STATE.md](PROJECT_STATE.md) | 当前进度 |
| [docs/STAGE_ROADMAP.md](docs/STAGE_ROADMAP.md) | Stage 0–11 路线图 |
| [docs/DATA_MODEL.md](docs/DATA_MODEL.md) | JSON 数据结构 |
| [docs/governance/](docs/governance/) | 治理协议 |

## 技术栈（规划）

- 后端：Python、FastAPI、SQLite、FFmpeg、Pydantic
- 前端：React、Vite、TypeScript、wavesurfer.js
- Round 00 仅占位，未安装完整依赖

## 当前默认假设

1. 中文文档为主，个人本地单用户使用
2. ASR/LLM 均通过 Adapter 可替换
3. 非破坏式编辑：原音频只读，切点存 JSON
4. 优先半自动 + 人工校正，不追求首轮全自动
