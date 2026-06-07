# 项目用户体验测试前置盘点报告

> 生成时间：2026-06-07  
> 盘点 Agent：用户体验测试前置盘点轮  
> 仓库路径：`audiobook-cleaner-lab`  
> 证据来源：文件扫描、CLI/API 验证、浏览器真实巡检（cursor-ide-browser）

---

## 1. 本轮任务范围

### 本轮做了什么

- 扫描仓库结构与关键配置文件
- 阅读 README、PROJECT_STATE、STAGE_ROADMAP、DATA_MODEL、UI_DESIGN 等文档
- 识别技术栈、用户角色、已实现 vs 规划功能
- 执行本地环境检查、Python unittest、前端 build、Playwright smoke、agent_gate
- 启动本地 API（:8000）与 Web（:5173），使用浏览器工具巡检 Review 页
- 测试 API 健康检查、review-data、音频只读服务、404 错误态、保存 Review 交互
- 生成本报告，供后续个性化测试 Prompt 复用

### 本轮未做什么

- 未修改业务代码、数据库、UI
- 未调用真实付费 ASR/LLM API
- 未执行真实 FFmpeg 导出（仅 `--dry-run`）
- 未部署生产环境
- 未提交 Git

---

## 2. 仓库结构摘要

### 2.1 根目录关键文件存在性

| 路径 | 状态 |
|------|------|
| `README.md` | ✅ 存在 |
| `package.json` | ✅ 存在（根 + `apps/web/`） |
| `package-lock.json` | ✅ 存在 |
| `pnpm-lock.yaml` / `yarn.lock` | ❌ 不存在 |
| `pyproject.toml` | ✅ 存在 |
| `requirements.txt` | ❌ 不存在（依赖在 pyproject.toml） |
| `.env.example` | ✅ 存在 |
| `.env` | 未读取（遵守安全规则） |
| `AGENTS.md` / `agent.md` | ✅ 存在 |
| `tsconfig.json` | ✅ `apps/web/tsconfig.json` |
| `vite.config.ts` | ✅ `apps/web/vite.config.ts` |
| `playwright.config.ts` | ✅ `apps/web/playwright.config.ts` |
| `docker-compose*` / `Dockerfile` | ❌ 不存在 |
| `.github/` | ❌ 不存在 |
| `prisma/` / `database/` / `migrations/` | ❌ 不存在 |

### 2.2 主要目录

```
audiobook-cleaner-lab/
├── apps/
│   ├── api/          # FastAPI 后端（Review + 音频只读）
│   └── web/          # React + Vite + TypeScript 前端
├── packages/         # Python 核心流水线模块
│   ├── asr_core/
│   ├── text_core/
│   ├── alignment_core/
│   ├── llm_core/
│   ├── audio_core/
│   └── feedback_core/
├── scripts/          # CLI 与运维脚本（23 个）
├── tests/            # Python unittest（8 个测试文件）
├── apps/web/tests/   # Playwright E2E smoke
├── data/           # 本地工作区（gitignore，含演示数据）
├── docs/           # 设计、治理、测试、MCP 文档
├── rounds/         # Stage/Round 推进记录（Round 00–16 相关）
├── prompts/        # LLM system prompt
├── config/         # 文本清洗配置示例
└── .cursor/        # MCP、Rules、Skills
```

### 2.3 项目类型判断

**全栈本地工具 + CLI 流水线**：Python 后端处理音频/文本流水线，React Web 提供 Review 审核台，无独立移动端/桌面端/插件。

---

## 3. 项目基本信息判断

| 维度 | 判断（附证据） |
|------|----------------|
| **项目名称** | `audiobook-cleaner-lab`（README、pyproject.toml） |
| **一句话定位** | 个人有声书原始录音 + 原文文本 → ASR/对齐/LLM 机切建议 → 人工 Review → FFmpeg 导出的专用清洗流水线（README L7–9） |
| **目标用户** | 自行录制中文有声书的个人创作者/后期操作者（PROJECT_VISION、README） |
| **主要解决问题** | 非破坏式识别并删除口误、重读、废话片段，保留可发布连续音频（非通用 DAW） |
| **成熟度** | **D — 有部分核心功能**（mock 主链路端到端可跑；Review UI 可用；真实 API/SQLite/完整 UI 未齐） |
| **方向混乱/文档脱节** | **轻度存在**：`UI_DESIGN.md` 规划多页面，代码仅单页 Review；`repo_protocol_standard.yaml` 写 SQLite，代码仍纯 JSON；Stage 12 进行中但 Round 12 文件缺失 |
| **最核心用户价值** | 半自动「机切建议 + 网页试听确认 + cut_plan 导出」降低个人有声书后期人工成本 |
| **最核心风险** | mock ASR/LLM 与真实场景差距未知；波形编辑器当前浏览器实测失败，影响切点微调；无项目/章节导航 UI，新用户难以自助发现入口 |

---

## 4. 技术栈与运行方式

### 4.1 语言与框架

| 层 | 技术 |
|----|------|
| 后端 | Python 3.10+、FastAPI、Pydantic、Uvicorn |
| 前端 | React 18、Vite 5、TypeScript 5、wavesurfer.js 7 |
| 音视频 | FFmpeg（CLI 导出） |
| Agent/工具 | Node.js 18+（MCP proxy、Playwright、Stitch SDK） |

### 4.2 数据层

| 类型 | 状态 |
|------|------|
| 本地 JSON 文件 | ✅ 已实现（`data/projects/`、`transcripts/`、`cut_plans/` 等） |
| SQLite | 📋 文档规划，代码未实现 |
| Redis / PostgreSQL / MongoDB / Prisma | ❌ 未使用 |

### 4.3 外部服务（仅配置痕迹，本轮未调用）

| 服务 | 状态 |
|------|------|
| OpenAI 兼容 LLM API | 骨架 `OpenAiCompatibleAdapter` 存在；无 Key 时 `real_api_check.py` exit 2 |
| 真实 ASR（Whisper 等） | 仅 Mock + ImportTranscript Adapter |
| Stitch API | MCP 设计工具，需 `STITCH_API_KEY` |
| GitHub API | MCP，需 `GITHUB_TOKEN` |
| 对象存储 / 支付 / 邮件 | ❌ 未发现 |

### 4.4 部署方式

| 方式 | 状态 |
|------|------|
| 本地开发 | ✅ `scripts/start_local.sh` |
| Docker / Compose | ❌ 不存在 |
| CI/CD（GitHub Actions 等） | ❌ 不存在 |
| 云平台配置 | ❌ 不存在 |

### 4.5 测试体系

| 类型 | 状态 |
|------|------|
| Python unittest | ✅ 31 tests，`tests/test_*.py` |
| Playwright E2E | ✅ 5 smoke tests，`apps/web/tests/smoke.spec.ts` |
| Vitest / Jest / Cypress | ❌ 未配置 |
| ESLint / 独立 lint | ❌ 未配置 |
| pytest | ❌ 未列入依赖（项目用 unittest） |

### 4.6 本地运行方式

```bash
# 推荐
bash scripts/start_local.sh
# 或分拆
.venv/bin/python -m uvicorn apps.api.main:app --host 127.0.0.1 --port 8000
cd apps/web && npm run dev
```

- API：`http://127.0.0.1:8000`
- Web：`http://localhost:5173`（Vite 绑定 localhost；`127.0.0.1:5173` 在本机实测不可达）
- Review 入口：`http://localhost:5173/?project_id=book_001&chapter_id=chapter_001`

---

## 5. 当前成熟度判断

**等级：D（有部分核心功能）**

依据：

| 能力 | 状态 |
|------|------|
| 仓库骨架与治理 | ✅ 完整 |
| CLI mock 流水线（导入→ASR→清洗→对齐→LLM→导出 dry-run→反馈） | ✅ 可运行 |
| FastAPI Review API | ✅ 已实现 |
| Review Web UI（三栏 + 决策） | ✅ 基本可用 |
| 波形编辑器 | ⚠️ UI 存在，浏览器实测 WaveSurfer 初始化失败 |
| 项目/章节选择页 | 📋 仅文档规划 |
| 真实 LLM/ASR | 📋 Adapter 骨架 / 未配置 Key |
| SQLite 元数据 | 📋 仅文档 |
| 一键验收门禁 | ✅ `agent_gate.py` 通过 |
| 生产部署能力 | ❌ 未具备 |

---

## 6. 已识别功能清单

### 6.1 普通用户功能

| 功能 | 实现状态 | 说明 |
|------|----------|------|
| 打开 Review 审核页 | ✅ 已实现 | 需 URL 参数 `project_id` + `chapter_id` |
| 查看原文 / ASR segments | ✅ 已实现 | 三栏布局，点击 segment 切换 |
| 查看 LLM 机切建议 | ✅ 已实现 | action、reason、confidence |
| 人工确认 keep/delete/uncertain | ✅ 已实现 | 三按钮 + 决策摘要 |
| 保存 Review 生成 cut_plan | ✅ 已实现 | 浏览器实测「已保存 cut_plan (delete: 4, keep: 0)」 |
| 波形试听与切点拖动 | ⚠️ 部分 | 按钮存在；波形加载失败，播放/拖动不可用 |
| 保存波形 cut_plan 微调 | ⚠️ UI 存在 | 依赖波形 ready，当前受阻 |
| 项目/章节浏览与创建 | 📋 规划 | `UI_DESIGN.md` 有设计，无页面 |
| Web 内导出音频 | 📋 规划 | 仅 CLI `run_export.py` |
| 登录注册 | ❌ 不适用 | 本地单用户工具，无认证 |

### 6.2 管理员 / 维护者功能

**未发现**独立管理后台。维护操作通过 CLI 脚本与 `data/` 目录文件完成。

### 6.3 开发者 / 操作者功能

| 脚本/命令 | 用途 |
|-----------|------|
| `scripts/start_local.sh` | 一键启动 API + Web，自动 seed 演示章节 |
| `scripts/seed_demo_chapter.py` | 生成 book_001/chapter_001 mock 数据 |
| `scripts/import_manifest.py` | 创建项目 / 添加章节 |
| `scripts/run_asr.py` | ASR mock |
| `scripts/run_normalize.py` | 文本清洗 |
| `scripts/run_align.py` | 对齐 |
| `scripts/run_llm_cut.py` | LLM 机切 mock |
| `scripts/run_export.py` | FFmpeg 导出（支持 `--dry-run`） |
| `scripts/run_feedback.py` | 反馈分析 |
| `scripts/batch_process.py` | 多章节批处理 |
| `scripts/auto_advance.py` | Agent 自动推进入口 |
| `scripts/agent_gate.py` | 验收门禁 |
| `scripts/real_api_check.py` | 真实 LLM API 检查（需 Key） |
| `scripts/check_environment.py` | 环境检查 |
| `scripts/check_repo.py` | 仓库骨架检查 |
| `npm run build` / `npm run test` | 前端构建与 Playwright |
| `npm run check:mcp` / `check:stitch` | MCP 配置检查 |

### 6.4 API 功能

| 方法 | 路径 | 用途 | 认证 | 本地可测 |
|------|------|------|------|----------|
| GET | `/api/health` | 健康检查 | 无 | ✅ |
| GET | `/api/projects/{pid}/chapters/{cid}/review-data` | Review 页数据 | 无 | ✅ |
| GET | `/api/projects/{pid}/chapters/{cid}/cut-plan` | 获取 cut_plan | 无 | ✅ |
| PUT | `/api/projects/{pid}/chapters/{cid}/cut-plan` | 更新 cut_plan | 无 | ✅（未浏览器逐项测） |
| POST | `/api/projects/{pid}/chapters/{cid}/review` | 保存 user_review | 无 | ✅（浏览器保存成功） |
| GET | `/api/audio/{path}` | 只读音频（`data/raw_audio/`、`data/exports/`） | 无 | ✅ HTTP 200 |

### 6.5 数据处理功能

**Pipeline（CLI，mock 模式）**：

```
导入 manifest → ASR(mock) → 文本清洗 → 对齐 → LLM 机切(mock)
    → [Web Review] → cut_plan.json → FFmpeg 导出 → 反馈分析
```

- 数据存于 `data/` 各子目录（JSON + wav/mp3）
- `seed_demo_chapter.py` 可一键生成演示链路数据
- `batch_process.py` 支持多章节批处理与 `--auto-review`

### 6.6 AI / Agent 功能

| 维度 | 状态 |
|------|------|
| ASR | `MockAsrAdapter`、`ImportTranscriptAdapter` |
| LLM | `MockLlmAdapter`（默认）、`OpenAiCompatibleAdapter`（需 Key） |
| Prompt | `prompts/llm_cut_decision/system_openai.md` |
| 审核机制 | confidence < 0.75 标 uncertain；Web 人工确认 |
| 失败处理 | mock 不调用外部；真实 API 无 Key 时 `real_api_check` HARD_BLOCK |
| Agent 自动推进 | `auto_advance.py`、`agent_gate.py` |
| Stitch 设计 MCP | 配置存在，需 `STITCH_API_KEY` |

---

## 7. 本地启动与验证结果

### 7.1 依赖安装

| 项 | 结果 |
|----|------|
| `.venv` | ✅ 已存在 |
| `apps/web/node_modules` | ✅ 已存在 |
| 系统 `python3`（无 venv） | ⚠️ FastAPI 未安装 |
| `.venv/bin/python` | ✅ FastAPI 等已安装 |

### 7.2 环境变量检查

| 变量 | `.env.example` | 本轮使用 |
|------|----------------|----------|
| `LLM_API_KEY` | 可选 | 未配置；`real_api_check` blocked |
| `STITCH_API_KEY` | 可选 | 未测试 Stitch MCP 调用 |
| `GITHUB_TOKEN` | 可选 | 未用于本轮 |

### 7.3 数据库初始化

不适用（无数据库）。执行 `init_data_dirs.py` 逻辑已嵌入 `start_local.sh`。

### 7.4 Lint 结果

**命令不存在**。根 `package.json` 与 `apps/web/package.json` 均无 `lint` 脚本，无 ESLint 配置。

### 7.5 Typecheck 结果

通过 `npm run build` 间接验证：`tsc -b` 成功（见 7.6）。

### 7.6 Build 结果

```
cd apps/web && npm run build
✓ tsc -b && vite build 成功（419ms）
产物：dist/index.html, dist/assets/index-*.js (206KB)
```

### 7.7 Test 结果

| 套件 | 命令 | 结果 |
|------|------|------|
| Python unittest | `.venv/bin/python -m unittest discover -s tests` | ✅ 31 passed |
| Playwright smoke | `cd apps/web && npm run test` | ✅ 5 passed |
| pytest | `python -m pytest` | ❌ 模块未安装 |
| agent_gate | `.venv/bin/python scripts/agent_gate.py` | ✅ 全部通过 |

### 7.8 Dev Server 结果

| 服务 | 结果 |
|------|------|
| API `:8000` | ✅ `{"status":"ok"}` |
| Web `:5173` | ✅ `localhost` 返回 200；`127.0.0.1:5173` 连接失败 |
| `start_local.sh` | 未整脚本跑（分拆启动成功） |
| 演示数据 seed | ✅ `book_001/chapter_001` 已存在 |

---

## 8. 界面 / 页面 / 交互巡检结果

**本轮使用浏览器工具**：`cursor-ide-browser`（真实页面、截图、可访问性快照）。

### 8.1 路由与页面

| 路由/URL | 实际行为 | 状态 |
|----------|----------|------|
| `/` | 渲染 Review 页，默认 `book_001/chapter_001` | ✅ |
| `/?project_id=book_001&chapter_id=chapter_001` | 加载 4 segments，三栏完整 | ✅ |
| `/?project_id=nonexistent&chapter_id=chapter_001` | 显示加载失败，含服务器绝对路径 | ⚠️ 错误态可用但暴露路径 |
| `/review`、`/admin`、`/workbench`、`/preview` | SPA fallback，同 Review 壳 | ✅ 无 500（smoke 验证） |

**未发现独立页面**：项目选择、章节列表、导出页、管理后台。

### 8.2 Review 页巡检明细

| 检查项 | 结果 |
|--------|------|
| 页面可打开 | ✅ |
| 明显报错 | ⚠️ 波形区红色错误 |
| 空白页 | ❌ 无 |
| 404 | ❌ 无（错误以文案展示） |
| Console error | ✅ 本轮未捕获（Playwright smoke 也通过） |
| 布局 | ✅ 桌面三栏正常；移动端 375px 变为单列堆叠，基本可读 |
| 文案解释用途 | ⚠️ 有章节/segment 信息，但无「这是什么工具」引导 |
| 按钮可点击 | ✅ 保存 Review 有效 |
| 表单输入 | N/A（无文本表单） |
| 操作反馈 | ✅ 保存后绿色「已保存 cut_plan…」 |
| 空状态 | 未测（演示数据始终存在） |
| 错误状态 | ⚠️ 原始 JSON + 绝对路径 |
| 加载状态 | ✅ 「加载中…」 |
| 下一步指引 | ⚠️ 弱（新用户不知 project_id 从哪来） |

### 8.3 波形区关键发现

- 页面底部显示：**「波形加载失败: Error: WaveSurfer is not initialized」**
- 播放/暂停、播放切点前后 2 秒按钮存在但波形未 ready
- 删除区间图例与区域 UI 框架存在
- 演示音频为 1 秒静音 wav（`seed_demo_chapter.py` 生成），可能影响波形体验

---

## 9. 用户角色与用户路径

### 9.1 用户角色

| 角色 | 描述 |
|------|------|
| **有声书录制者/后期操作者** | 主用户：上传素材、跑流水线、Review、导出 |
| **开发者/Agent 操作者** | 维护脚本、跑门禁、扩展 Adapter |
| **UI/设计协作者** | 通过 Stitch 提供设计输入（可选） |

无多租户、无管理员角色、无登录。

### 9.2 用户路径

#### 路径 01：首次访问

```
路径编号：UP-01
路径名称：首次打开 Review 页
用户角色：新用户
入口：http://localhost:5173/
操作步骤：打开首页 → 等待加载 → 浏览三栏
成功标准：理解这是有声书 Review 工具，能看到 segment 与模型建议
当前是否可完成：部分
阻塞点：无项目背景说明；默认依赖已 seed 的 demo；无导航到其他章节
风险：用户不知道要准备自己的 project_id
后续是否值得重点测试：是
```

#### 路径 02：核心 Review 闭环

```
路径编号：UP-02
路径名称：查看建议 → 人工确认 → 保存 cut_plan
用户角色：后期操作者
入口：/?project_id=book_001&chapter_id=chapter_001
操作步骤：选 segment → 确认/删除/不确定 → 点击「保存 Review & cut_plan」
成功标准：出现保存成功提示，cut_plan 写入 data/
当前是否可完成：是
阻塞点：无
风险：低
后续是否值得重点测试：是（最高优先级）
```

#### 路径 03：波形微调

```
路径编号：UP-03
路径名称：波形试听与拖动切点
用户角色：后期操作者
入口：Review 页底部波形区
操作步骤：加载波形 → 播放切点 → 拖动删除区间 → 保存微调
成功标准：波形显示、可播放、可拖动并保存
当前是否可完成：否
阻塞点：WaveSurfer 未初始化
风险：切点无法听感微调，核心价值链受损
后续是否值得重点测试：是（最高优先级）
```

#### 路径 04：数据输入（自有素材）

```
路径编号：UP-04
路径名称：导入真实章节音频与原文
用户角色：录制者
入口：CLI `import_manifest.py` + 放置 data/raw_audio、data/source_text
操作步骤：create-project → add-chapter → run_asr → … → 打开 Review URL
成功标准：Review 页展示真实章节数据
当前是否可完成：是（CLI），Web 无导入 UI
阻塞点：需读 README；无 Web 上传
风险：CLI 门槛高
后续是否值得重点测试：是
```

#### 路径 05：数据输出（导出）

```
路径编号：UP-05
路径名称：导出清洗后音频
用户角色：后期操作者
入口：CLI `run_export.py`
操作步骤：完成 Review → run_export（或 --dry-run）
成功标准：生成 mp3 或 dry-run 输出 ffmpeg 命令
当前是否可完成：是（CLI dry-run 实测成功）
阻塞点：Web 无导出按钮
风险：用户可能不知下一步
后续是否值得重点测试：是
```

#### 路径 06：管理/批处理

```
路径编号：UP-06
路径名称：多章节批处理
用户角色：开发者/重度用户
入口：`batch_process.py --project-id book_001 --auto-review`
操作步骤：配置多章节 → 批处理 → 检查产物
成功标准：多章节状态推进
当前是否可完成：是（代码+round 文档），本轮未实测多章
阻塞点：无 Web 队列 UI
风险：低
后续是否值得重点测试：中
```

#### 路径 07：错误恢复

```
路径编号：UP-07
路径名称：无效 project/chapter
用户角色：任意
入口：/?project_id=nonexistent&chapter_id=chapter_001
操作步骤：打开错误 URL
成功标准：友好提示 + 引导下一步
当前是否可完成：部分
阻塞点：错误信息含绝对路径与原始 JSON
风险：泄露本机路径；用户不知如何修复
后续是否值得重点测试：是
```

#### 路径 08：新手上手

```
路径编号：UP-08
路径名称：按 README 从零跑通
用户角色：新开发者
入口：README 快速开始
操作步骤：venv → pip → npm → start_local.sh → 打开 Review
成功标准：15 分钟内看到 Review 页有数据
当前是否可完成：是（有 .venv 时）
阻塞点：系统 python3 无 FastAPI；需知 localhost vs 127.0.0.1
风险：环境文档分散
后续是否值得重点测试：是
```

---

## 10. 初步测试用例素材

### A. 首次访问 / 首次使用

```
用例编号：TC-A01
用例名称：首页默认可加载演示章节
项目模块：apps/web Review
用户角色：新用户
前置条件：已执行 seed_demo_chapter 或 start_local.sh
测试步骤：打开 http://localhost:5173/ → 等待加载
预期结果：显示「第一章 · N segments · engine: mock」，三栏有内容
当前是否可测：是
当前阻塞点：无
优先级：P1
备注：同时检查是否有项目定位说明
```

```
用例编号：TC-A02
用例名称：无 demo 数据时的空状态
项目模块：Review API + UI
用户角色：新用户
前置条件：删除 data/projects/book_001 后启动
测试步骤：打开默认 URL
预期结果：友好空状态 + 引导 seed 或导入
当前是否可测：是
当前阻塞点：空状态 UX 未专门设计
优先级：P2
```

### B. 核心功能闭环

```
用例编号：TC-B01
用例名称：保存 Review 生成 cut_plan
项目模块：Review API + UI
用户角色：后期操作者
前置条件：演示章节已对齐+LLM
测试步骤：修改若干 segment 决策 → 保存 Review
预期结果：成功提示；data/cut_plans/ 与 user_review 更新
当前是否可测：是
当前阻塞点：无
优先级：P0
```

```
用例编号：TC-B02
用例名称：波形切点微调并保存
项目模块：WaveformEditor
用户角色：后期操作者
前置条件：波形正常加载
测试步骤：拖动删除区间 → 保存波形微调
预期结果：cut_plan delete_ranges 更新
当前是否可测：否
当前阻塞点：WaveSurfer 初始化失败
优先级：P0
```

### C. 数据输入

```
用例编号：TC-C01
用例名称：CLI 导入新章节
项目模块：import_manifest.py
用户角色：录制者
前置条件：本地 wav + txt
测试步骤：create-project → add-chapter → 跑 ASR 流水线
预期结果：chapter_manifest.json 与后续 JSON 生成
当前是否可测：是
当前阻塞点：需自备音频
优先级：P1
```

### D. 数据输出

```
用例编号：TC-D01
用例名称：FFmpeg 导出 dry-run
项目模块：run_export.py
用户角色：后期操作者
前置条件：已有 cut_plan
测试步骤：run_export --dry-run
预期结果：输出 ffmpeg 命令与 deleted_sec
当前是否可测：是（本轮已验证）
当前阻塞点：无
优先级：P1
```

### E. 权限与身份

**不适用** — 本地单用户，无登录/权限系统。

### F. 错误状态

```
用例编号：TC-F01
用例名称：不存在章节 API 404
项目模块：Review API
用户角色：任意
前置条件：API 运行
测试步骤：GET review-data 无效 project
预期结果：HTTP 404，UI 友好错误（不含绝对路径）
当前是否可测：是
当前阻塞点：UI 暴露绝对路径
优先级：P2
```

### G. 空状态

```
用例编号：TC-G01
用例名称：cut_plan 不存在时前端行为
项目模块：ReviewPage loadCutPlan
用户角色：后期操作者
前置条件：仅有 llm_decision 无 cut_plan
测试步骤：打开 Review
预期结果：从 segments 构建初始 delete_ranges
当前是否可测：是
当前阻塞点：需构造数据
优先级：P2
```

### H. 移动端 / 小屏幕

```
用例编号：TC-H01
用例名称：375px 宽度可读性
项目模块：apps/web styles
用户角色：后期操作者
前置条件：Dev server 运行
测试步骤：窄屏打开 Review → 滚动三栏
预期结果：内容可读、按钮可点
当前是否可测：是（本轮快照验证单列堆叠）
当前阻塞点：无严重阻断
优先级：P3
```

### I. 性能与加载

```
用例编号：TC-I01
用例名称：Review 数据加载时间
项目模块：Review API
用户角色：任意
前置条件：演示章节
测试步骤：打开 Review，记录首屏时间
预期结果：< 2s（mock 数据）
当前是否可测：是
当前阻塞点：无
优先级：P3
```

### J. 可访问性与可读性

```
用例编号：TC-J01
用例名称：segment 列表键盘可达性
项目模块：ReviewPage
用户角色：后期操作者
前置条件：页面加载
测试步骤：Tab 遍历 segment 与按钮
预期结果：可聚焦、可操作
当前是否可测：是
当前阻塞点：segment 为 li 非 button，可访问性待验证
优先级：P3
```

### K. 管理后台 / 维护功能

```
用例编号：TC-K01
用例名称：agent_gate 一键验收
项目模块：scripts/agent_gate.py
用户角色：开发者
前置条件：.venv + node_modules
测试步骤：python scripts/agent_gate.py
预期结果：全部通过
当前是否可测：是（本轮已通过）
当前阻塞点：无
优先级：P2
```

### L. 部署与交付

```
用例编号：TC-L01
用例名称：生产构建产物可预览
项目模块：apps/web build
用户角色：开发者
前置条件：npm run build
测试步骤：npm run preview
预期结果：Review 页在 preview 模式可访问 API
当前是否可测：是
当前阻塞点：preview 需同时起 API
优先级：P2
```

```
用例编号：TC-L02
用例名称：Docker 一键部署
项目模块：部署
用户角色：运维
前置条件：N/A
测试步骤：docker compose up
预期结果：服务可用
当前是否可测：不适用
当前阻塞点：无 Docker 配置
优先级：P4
```

---

## 11. 已发现问题清单

### P0 阻塞

*本轮未发现 P0*（在 `.venv` + 已安装依赖前提下，主链路可启动）。

```
问题编号：ISS-P0-01（条件性）
问题等级：P0（仅当无 .venv 时）
问题位置：环境 / README 快速开始
复现方式：系统 python3 直接运行 check_environment 或 uvicorn
实际表现：FastAPI 未安装，无法启动 API
期望表现：文档明确必须先 activate .venv 或 pip install
可能原因：依赖装在 .venv 而非系统 Python
建议修复方向：README 强调 .venv；check_environment 提示 activate
是否需要后续测试 Prompt 覆盖：是
```

### P1 严重

```
问题编号：ISS-P1-01
问题等级：P1
问题位置：apps/web/src/components/WaveformEditor.tsx
复现方式：打开 Review 页，等待加载完成
实际表现：「波形加载失败: Error: WaveSurfer is not initialized」
期望表现：波形渲染、播放/拖动切点可用
可能原因：wavesurfer v7 初始化时序；演示静音短 wav；destroy/recreate 竞态
建议修复方向：检查 ws.ready 门禁、音频 URL、wavesurfer 7 API 用法
是否需要后续测试 Prompt 覆盖：是
```

```
问题编号：ISS-P1-02
问题等级：P1
问题位置：整体产品导航
复现方式：新用户仅打开 Web，不读 README
实际表现：无项目/章节选择，必须手写 URL 参数
期望表现：可选书/章列表或向导
可能原因：Round 06 MVP 仅实现单页
建议修复方向：实现 UI_DESIGN 中的项目/章节页或最小导航
是否需要后续测试 Prompt 覆盖：是
```

### P2 中等

```
问题编号：ISS-P2-01
问题等级：P2
问题位置：ReviewPage 错误展示
复现方式：project_id=nonexistent
实际表现：加载失败文案含本机绝对路径与原始 JSON
期望表现：用户友好简短错误 + 操作建议
可能原因：直接 String(e) 展示 API 响应
建议修复方向：解析 detail 字段，隐藏路径
是否需要后续测试 Prompt 覆盖：是
```

```
问题编号：ISS-P2-02
问题等级：P2
问题位置：Web 导出能力
复现方式：完成 Review 后寻找导出按钮
实际表现：仅 CLI 可导出
期望表现：UI_DESIGN 中的导出入口或说明链接
可能原因：Round 08 仅 CLI
建议修复方向：增加导出按钮或引导文案
是否需要后续测试 Prompt 覆盖：是
```

```
问题编号：ISS-P2-03
问题等级：P2
问题位置：Vite dev server 绑定
复现方式：访问 http://127.0.0.1:5173
实际表现：连接失败；localhost 正常
期望表现：127.0.0.1 与 localhost 均可（或文档说明）
可能原因：Vite 默认 host localhost
建议修复方向：vite server.host: true 或文档统一写 localhost
是否需要后续测试 Prompt 覆盖：是
```

```
问题编号：ISS-P2-04
问题等级：P2
问题位置：演示音频质量
复现方式：seed_demo_chapter 后试听
实际表现：1 秒静音 wav
期望表现：带可听内容的示例，便于验证波形/播放
可能原因：seed 脚本用零帧占位
建议修复方向：生成短 tone 或文档说明需真实音频
是否需要后续测试 Prompt 覆盖：是
```

### P3 轻微

```
问题编号：ISS-P3-01
问题等级：P3
问题位置：Review 页 header
复现方式：首次访问
实际表现：仅标题 + MVP 徽章，无工具说明
期望表现：一句话说明用途与下一步
可能原因：MVP 极简 UI
建议修复方向：增加 subtitle 或帮助链接
是否需要后续测试 Prompt 覆盖：是
```

```
问题编号：ISS-P3-02
问题等级：P3
问题位置：SPA 路由
复现方式：访问 /admin、/workbench
实际表现：与首页相同 Review 壳，无真实后台
期望表现：404 或明确「未实现」
可能原因：无 react-router，smoke 仅测无 500
建议修复方向：路由说明或 NotFound 页
是否需要后续测试 Prompt 覆盖：可选
```

### P4 建议

```
问题编号：ISS-P4-01
问题等级：P4
问题位置：工程化
复现方式：查找 lint/CI
实际表现：无 ESLint、无 GitHub Actions
期望表现：基础 CI 跑 unittest + playwright + build
可能原因：Stage 早期
建议修复方向：添加最小 CI workflow
是否需要后续测试 Prompt 覆盖：可选
```

```
问题编号：ISS-P4-02
问题等级：P4
问题位置：SQLite 元数据
复现方式：阅读治理文档 vs 代码
实际表现：仍纯 JSON 文件
期望表现：文档描述的 SQLite 元数据
可能原因：后续 Stage 规划
建议修复方向：实现或更新文档
是否需要后续测试 Prompt 覆盖：否
```

---

## 12. 不可测、缺失或仅规划的功能

| 功能 | 类型 | 说明 |
|------|------|------|
| 项目选择页 | 文档规划 | `UI_DESIGN.md` §1，代码无 |
| 章节选择页 | 文档规划 | `UI_DESIGN.md` §2 |
| 快捷键 K/R/U/Space | 文档规划 | `UI_DESIGN.md` §4 |
| Web 导出按钮 | 文档规划 | CLI 已实现 |
| 真实 ASR API | 未实现 | 仅 mock/import |
| 真实 LLM 流水线 | 需 Key | `real_api_check` exit 2 |
| SQLite | 文档规划 | 治理 yaml、PIPELINE_DESIGN |
| Docker 部署 | 未实现 | 无配置文件 |
| CI/CD | 未实现 | 无 `.github/` |
| 用户认证 | 不适用 | 本地工具 |
| Stitch 实机设计生成 | 需 Key | 本轮未调用 |
| 批处理 Web 队列 | 文档规划 | CLI 存在 |

---

## 13. 文档与代码不一致之处

| 文档描述 | 代码现状 |
|----------|----------|
| `UI_DESIGN.md` 多页面结构 | 仅 `App.tsx` → `ReviewPage` 单页 |
| `repo_protocol_standard.yaml` backend 含 SQLite | 无 SQLite 代码 |
| `PIPELINE_DESIGN.md` SQLite 元数据 | 全 JSON 文件 |
| README Review URL 用 `127.0.0.1:5173` | Vite 实测需 `localhost:5173` |
| PROJECT_STATE Round 12 已完成 | `rounds/` 无 `round-12-*.md` 文件 |
| smoke 测试 `/admin` 等路由 | 无真实页面，仅 SPA 回退 |
| Stage 0–11 完成 vs Stage 12 进行中 | 状态一致，但 UI 仍大量 MVP |

---

## 14. 部署与交付可用性判断

| 维度 | 判断 |
|------|------|
| 本地开发交付 | ✅ 成熟（`start_local.sh`、seed、agent_gate） |
| 生产构建 | ✅ `npm run build` 成功 |
| 容器化 | ❌ 不可用 |
| 自动化 CI | ❌ 不可用 |
| 环境变量文档 | ✅ `.env.example` 清晰 |
| 一键验收 | ✅ `agent_gate.py` |
| 真实 API 验收 | ⚠️ 需用户配置 `LLM_API_KEY` |

**结论**：适合**个人本地工作站**交付，尚不具备标准化线上部署与运营能力。

---

## 15. 适合下一阶段重点测试的路径

1. **UP-02 核心 Review 闭环**（保存决策、cut_plan 一致性）— 已部分验证，需加数据文件断言  
2. **UP-03 波形微调**（WaveSurfer 加载、播放、拖动、保存）— 当前最大 UX 断裂点  
3. **UP-04 + UP-05 CLI 导入到导出**（真实或更长 demo 音频端到端）— 验证非 mock 素材体验  

次要：**UP-07 错误恢复**、**UP-08 新手上手**（README 路径实测）。

---

## 16. 对后续个性化测试 Prompt 的建议

1. **聚焦单页 Review + CLI 组合**：不要假设有项目控制台；测试 Prompt 应包含 URL 参数构造与 CLI 前置步骤。  
2. **拆分「UI 审核」与「流水线 CLI」两条线**：Web 测交互与 API；CLI 测 JSON 产物与 ffmpeg dry-run。  
3. **波形问题单列回归套件**：加载、ready 状态、播放、region 拖动、保存 API 应对。  
4. **Mock vs Real 分档**：默认 mock；真实 LLM 测试需显式 Key 与费用警告。  
5. **错误态用例必含**：无效 project_id、API 未启动、无 cut_plan、静音/损坏音频。  
6. **使用 `localhost:5173` 而非 127.0.0.1** 访问前端。  
7. **验收命令写入 Prompt**：`agent_gate.py`、`npm run test`、关键 unittest。  
8. **区分 bug vs 未实现**：项目/章节页、导出按钮、快捷键属于规划缺口，非回归 bug。  

---

## 17. 附录：执行过的命令与结果摘要

| 命令 | 结果摘要 |
|------|----------|
| `python3 scripts/check_environment.py` | exit 1 — 系统 Python 无 FastAPI |
| `.venv/bin/python scripts/check_environment.py` | exit 0 — 全部通过 |
| `python3 scripts/check_repo.py` | exit 0 — 骨架通过 |
| `node scripts/check_mcp_config.js` | exit 0 — MCP 配置通过 |
| `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'` | 31 tests OK |
| `cd apps/web && npm run build` | exit 0 — 构建成功 |
| `cd apps/web && npm run test` | exit 0 — 5 Playwright passed |
| `.venv/bin/python scripts/seed_demo_chapter.py` | 章节已存在，跳过 |
| `.venv/bin/python scripts/agent_gate.py` | exit 0 — 门禁全部通过 |
| `.venv/bin/python scripts/run_export.py --project-id book_001 --chapter-id chapter_001 --dry-run` | exit 0 — deleted_sec: 1.72 |
| `.venv/bin/python scripts/real_api_check.py` | exit 2 — 无 LLM_API_KEY |
| `curl http://127.0.0.1:8000/api/health` | `{"status":"ok"}` |
| `curl http://127.0.0.1:8000/api/projects/book_001/chapters/chapter_001/review-data` | 4 segments, title 第一章 |
| `curl -w %{http_code} .../nonexistent/.../review-data` | 404 |
| `curl .../api/audio/data/raw_audio/book_001/chapter_001.wav` | 200 audio/wav |
| `curl http://localhost:5173/` | 200 |
| `curl http://127.0.0.1:5173/` | 连接失败 |
| `.venv/bin/python -m uvicorn apps.api.main:app --port 8000` | 后台运行成功 |
| `cd apps/web && npm run dev` | 后台运行成功，localhost:5173 |
| 浏览器导航 `localhost:5173/?project_id=book_001&chapter_id=chapter_001` | Review 加载，保存成功，波形失败 |
| 浏览器导航 `...?project_id=nonexistent...` | 加载失败，暴露绝对路径 |
| `python -m pytest tests/` | 失败 — pytest 未安装 |

### 问题统计

| 等级 | 数量 |
|------|------|
| P0 | 0（1 项条件性环境问题） |
| P1 | 2 |
| P2 | 4 |
| P3 | 2 |
| P4 | 2 |

---

*本报告基于 2026-06-07 仓库状态生成；后续代码变更后应重新盘点关键路径。*
