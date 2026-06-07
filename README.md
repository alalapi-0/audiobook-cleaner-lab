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
- Review 页: http://localhost:5173/?project_id=book_001&chapter_id=chapter_001（`127.0.0.1:5173` 亦可）

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

## Workspace MCP Servers

本仓库在 Cursor 中作为 **Workspace MCP Servers** 启用以下 6 个 MCP：

| MCP | 用途 |
|-----|------|
| **chrome-devtools** | 浏览器调试、console、network |
| **context7** | 第三方库/框架文档查询 |
| **filesystem** | 当前项目目录内文件读写与检查 |
| **github** | 仓库、提交、分支、issue、PR |
| **playwright** | 浏览器自动化与 E2E 验收 |
| **stitch** | UI 设计、原型、截图、HTML 导出 |

说明：

1. [`.cursor/mcp.json`](.cursor/mcp.json) 是本项目的 Workspace MCP 配置。
2. 修改配置后，Cursor 可能需要 **重启或 Reload Window** 才能识别。
3. **GitHub MCP** 需通过环境变量（如 `GITHUB_TOKEN`）提供 token，**不允许**写进仓库。
4. **filesystem MCP** 仅授权当前项目目录（`${workspaceFolder}`），不授权整盘或用户主目录。
5. 运行 `npm run check:mcp` 与 `npm run check:stitch` 可检查配置格式与安全规则。

详见 [AGENTS.md](AGENTS.md) 与 [docs/agent_skills/mcp_usage_skill.md](docs/agent_skills/mcp_usage_skill.md)。

## Stitch Design MCP

**Stitch** 是 Google 的 UI 设计能力，本项目将其作为 **设计输入层** 接入，供 Cursor / Codex / Agent 生成审核台、控制台等界面原型。

### 为什么使用

- 有声书 Review 审核台、项目控制台等 UI 需要一致的设计参考
- Stitch 可输出 screen、截图、HTML，减少 Agent 盲目改 UI
- 与 Playwright / chrome-devtools 验证闭环配合

### 配置 STITCH_API_KEY

```bash
cp .env.example .env
# 编辑 .env 填入 STITCH_API_KEY（勿提交 .env）
export STITCH_API_KEY=your_key_here   # 或在 Cursor 环境中设置
npm install
```

### 加载 MCP

1. 配置已写入 [`.cursor/mcp.json`](.cursor/mcp.json)（本地 stdio proxy）
2. **重启 Cursor** → Settings → MCP → 确认 `stitch` 已启用
3. `npm run check:stitch`

### 生成 UI 设计

1. 阅读 [docs/design/DESIGN.md](docs/design/DESIGN.md) 与 [docs/design/stitch/UI_TASKS.md](docs/design/stitch/UI_TASKS.md)
2. 使用 [PROMPT_TEMPLATES.md](docs/design/stitch/PROMPT_TEMPLATES.md) 通过 Stitch MCP 生成
3. 结果保存到 `docs/design/stitch/exports/`、`screenshots/`、`reviews/`

### 角色分工

| 角色 | 职责 |
|------|------|
| **Stitch** | 设计输入（原型、截图、HTML） |
| **Cursor** | 根据设计在 `apps/web/` 落地实现 |
| **Codex** | 用户视角测试，输出问题与改进任务 |

### 安全注意事项

- **不要**提交 `.env`
- **不要**把 key 写入代码或 `.cursor/mcp.json`
- **不要**用 Stitch 导出代码无审查覆盖业务代码
- 实现后必须用 Playwright 或 chrome-devtools 验证

### 常见问题

| 问题 | 处理 |
|------|------|
| stitch MCP 未连接 | 设置 `STITCH_API_KEY`，`npm install`，重启 Cursor |
| 无 Stitch 工具 | 检查 MCP 面板 server 名是否为 `stitch` |
| 不想用 Stitch | 直接用 `docs/UI_DESIGN.md` 与 `docs/design/stitch/UI_TASKS.md` 手写任务 |

详见 [docs/design/stitch/README.md](docs/design/stitch/README.md) 与 [STITCH_MCP_SETUP.md](docs/design/stitch/STITCH_MCP_SETUP.md)。

## Cursor Browser UI Workflow

本仓库已配置 Cursor Agent 通过 MCP 进行浏览器检查、Stitch 设计、UI 实现与回归验证。完整 Runbook：[docs/cursor_browser_ui_runbook.md](docs/cursor_browser_ui_runbook.md)。

### 1. 如何检查 MCP

```bash
npm run check:cursor-mcp
# 或
bash scripts/check_cursor_mcp_status.sh
```

同时可运行 `npm run check:mcp` 与 `npm run check:stitch` 检查配置格式与安全。

**注意**：上述脚本只检查 **CLI 层**；当前 Agent 对话线程是否暴露工具，须在对话中自行确认。见 [docs/cursor_tool_registry_check.md](docs/cursor_tool_registry_check.md)。

### 2. 为什么需要重启 Cursor

- 在 Settings 中**批准 MCP** 后，**旧 Agent 对话**可能仍停留在批准前的工具注册表，调用会报 `server does not exist`。
- **Multitask** 子 Agent 可能**不继承** Workspace MCP，浏览器任务易失败。
- 最稳定做法：**完全退出 Cursor** → 重开仓库 → **新建普通前台 Agent 对话** → **禁用 Multitask**。

### 3. UI 优化标准流程

1. 启动项目（`bash scripts/start_local.sh`）
2. 打开 Review 页面
3. **Before**：截图 + console + network
4. 查阅或调用 **Stitch** 设计
5. 修改 `apps/web/`（每轮一个 UI 切片）
6. 重新打开页面
7. **After**：console / network 检查
8. 运行 `npm run test` / `npm run build`
9. 用户要求时 commit / push

启动 Prompt 模板：[docs/prompts/CURSOR_UI_IMPLEMENTATION_PROMPT.md](docs/prompts/CURSOR_UI_IMPLEMENTATION_PROMPT.md)。

### 4. 微信页面特殊说明（本仓库不适用）

本仓库为**本地 Web 审核台**，不使用微信公众号已登录页面。若在其他项目操作微信已登录页：

- **必须**使用 `wechat-chrome-session`
- **禁止**用 Playwright 新开页面替代（无登录态）
- 遇到扫码 / 风控须停止并等待用户手动处理
