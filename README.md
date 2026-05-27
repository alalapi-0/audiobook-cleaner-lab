# audiobook-cleaner-lab

**个人有声书音频清洗与文本对齐剪辑工具**

## 项目说明

本项目用于将个人录制的中文有声书原始录音，结合正确原文文本，通过 ASR、文本对齐、大模型机切建议与人工校正，最终导出干净、连续、可发布的有声书音频。

这不是通用 DAW 剪辑软件，而是一条 **原文 + ASR + LLM + 人工 Review + FFmpeg** 的专用流水线。

## 当前状态

**Stage 0–11 / Round 00–11 已全部完成（mock 流水线可端到端运行）**

详见 [PROJECT_STATE.md](PROJECT_STATE.md)。

## 快速开始

### 1. 环境检查

```bash
python3 scripts/check_environment.py   # Python / FFmpeg / Node / FastAPI
python3 scripts/init_data_dirs.py
python3 scripts/check_repo.py
```

### 2. 安装依赖

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install fastapi uvicorn pydantic httpx

cd apps/web && npm install && cd ../..
```

### 3. 一键启动（API + Web）

```bash
bash scripts/start_local.sh
```

- API: http://127.0.0.1:8000
- Review 页: http://127.0.0.1:5173/?project_id=book_001&chapter_id=chapter_001

### 4. Mock 单章全流程（CLI）

```bash
# 导入（需本地放置 wav + txt，或使用测试目录）
python3 scripts/import_manifest.py create-project --project-id book_001 --title "示例有声书"
python3 scripts/import_manifest.py add-chapter \
  --project-id book_001 --chapter-id chapter_001 --title "第一章" \
  --audio data/raw_audio/book_001/chapter_001.wav \
  --text data/source_text/book_001/chapter_001.txt

python3 scripts/run_asr.py --project-id book_001 --chapter-id chapter_001
python3 scripts/run_normalize.py --project-id book_001 --chapter-id chapter_001
python3 scripts/run_align.py --project-id book_001 --chapter-id chapter_001
python3 scripts/run_llm_cut.py --project-id book_001 --chapter-id chapter_001
# Review 在 Web 完成，或批处理自动采纳 mock 建议：
python3 scripts/batch_process.py --project-id book_001 --auto-review --skip-export
python3 scripts/run_export.py --project-id book_001 --chapter-id chapter_001 --dry-run
python3 scripts/run_feedback.py --project-id book_001 --chapter-id chapter_001
```

## CLI 脚本一览

| 脚本 | 用途 |
|------|------|
| `import_manifest.py` | 创建项目 / 添加章节 |
| `run_asr.py` | ASR mock / import |
| `run_normalize.py` | 文本清洗 |
| `run_align.py` | 原文与 ASR 对齐 |
| `run_llm_cut.py` | LLM 机切建议（mock） |
| `run_api.py` | 启动 FastAPI |
| `run_export.py` | FFmpeg 导出（`--dry-run`） |
| `run_feedback.py` | 反馈分析 |
| `batch_process.py` | 多章节批处理 |
| `check_environment.py` | 环境检查 |
| `start_local.sh` | 一键启动 API + Web |

## 大文件与 Git 策略

- 真实音频、中间产物放在 `data/` 目录
- **`data/` 真实内容不进入 Git**
- 不调用真实付费 ASR/LLM API（当前为 mock Adapter）

## 快速导航

| 文档 | 用途 |
|------|------|
| [AGENTS.md](AGENTS.md) | AI Agent 工作规范 |
| [PROJECT_STATE.md](PROJECT_STATE.md) | 当前进度 |
| [docs/STAGE_ROADMAP.md](docs/STAGE_ROADMAP.md) | Stage 0–11 路线图 |
| [docs/DATA_MODEL.md](docs/DATA_MODEL.md) | JSON 数据结构 |

## 技术栈

- 后端：Python 3.10+、FastAPI、Pydantic、FFmpeg
- 前端：React、Vite、TypeScript、wavesurfer.js
- 存储：本地 JSON + `data/` 目录（SQLite 后续可选）

## 重要原则

1. **非破坏式编辑**：原音频只读，切点存 JSON
2. **LLM 不直接切音频**：仅文本层机切建议
3. **低置信不自动删**：`confidence < 0.75` 须人工确认
