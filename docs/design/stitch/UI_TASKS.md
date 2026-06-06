# Stitch 设计任务模板

面向 **audiobook-cleaner-lab**（有声书清洗 + Review 审核台）及通用后台场景。复制模板到 Stitch 对话或 `prompts/` 目录后按需修改。

---

## 1. 主控制台 Dashboard

**目标页面**：项目总览 / 章节进度

**目标用户**：有声书后期制作者

**必须包含**：

- 项目列表（书名、章节数、整体进度）
- 最近生成任务（ASR / 对齐 / LLM 机切 / 导出）
- 模式标记：`real_api` / `mock` / `dry-run`
- 最近产物路径摘要
- 失败任务列表与重试入口
- 进入 Review 审核台快捷入口

**布局**：左侧导航 + 主区卡片网格 + 顶栏状态

**中文文案示例**：「项目控制台」「最近任务」「失败重试」「进入审核」

**技术约束**：React + Vite；不生成营销落地页

**导出**：`exports/dashboard-{date}.html`，截图 `screenshots/dashboard-{date}.png`

---

## 2. 真实 API 生成任务页

**目标页面**：LLM 机切 / ASR 任务配置与结果

**必须包含**：

- Prompt / 参数输入区
- Provider / 模型选择
- `real_api` / `mock` 模式切换（明显标记）
- 生成状态（排队 / 进行中 / 完成 / 失败）
- 错误信息区
- 结果预览与保存
- 重试按钮

**本项目特化**：章节级任务；显示 `project_id` / `chapter_id`

---

## 3. 审核台 Review Workbench（核心）

**目标页面**：三栏文本 + 底栏波形 Review 页

**必须包含**（对齐 [UI_DESIGN.md](../../UI_DESIGN.md)）：

- 左：原文文本区（高亮对齐）
- 中：ASR segment 列表（点击跳转时间）
- 右：模型建议区（keep / delete / uncertain，confidence）
- 底：wavesurfer 波形 + 区间色块（绿/红/黄）
- 操作：确认 / 驳回 / 标记不确定 / 保存 / 导出
- 显示 `real_api` / `mock` 标记与文件路径
- 元数据：alignment status、日志摘要

**交互状态**：选中 segment、播放中、未保存提示、低置信高亮

**非目标**：多轨 DAW、登录权限

---

## 4. Debug / Observability 页面

**目标页面**：开发与运维可观测

**必须包含**：

- API health（FastAPI `/health` 或等价）
- 最近 console / network 错误摘要（占位 UI）
- 任务队列状态
- `data/` 关键 JSON 文件状态（manifest、cut_plan、user_review）
- 最近操作日志列表
- mock / real_api 模式指示

---

## 5. 音频波形审核台（本项目视觉审核）

> 有声书场景替代「图片/视频视觉审核台」

**目标页面**：以波形与区间为主的视觉审核

**必须包含**：

- 全章波形缩略图 + 可缩放时间轴
- 删除区间（红）、保留（绿）、不确定（黄）色块
- 当前播放位置与 segment 联动
- 切点前后 ±2s 试听按钮
- 章节元数据：时长、segment 数、低置信数量
- 通过 / 驳回 / 标记待听 / 导出 dry-run

---

## 6. 批处理 Gallery（章节批处理视图）

**目标页面**：多章节批处理状态一览

**必须包含**：

- 章节卡片 grid：标题、status、进度条
- 批处理队列：等待 / 运行 / 完成 / 失败
- 单章快捷入口：Review / 重跑 ASR / 重跑 LLM
- 批量导出状态

---

## 7. 导出 Workbench

**目标页面**：FFmpeg 导出与产物预览

**必须包含**：

- 导出参数（dry-run 开关）
- 输入：cut_plan / user_review 路径
- 导出进度与日志
- 输出文件路径与试听播放器
- 失败重试

---

## 通用模板（其他项目类型参考）

以下模板在本仓库中作为 **参考存档**，当前优先级低于 1–7。

### 8. 视觉结果审核台（图片/视频）

- 缩略图 grid、视频播放器、抽帧预览
- prompt 摘要、质量评分、一致性检查
- 通过 / 驳回 / 重新生成

### 9. 游戏资产 Gallery

- 角色图、sprite sheet、动画帧
- 透明背景 / 尺寸 / 帧对齐检查
- 导出游戏资产

### 10. 视频生成 Workbench

- 图片输入、文字 prompt、镜头列表
- 生成状态、视频结果、抽帧
- 单镜头重新生成

---

## 任务提交检查清单

- [ ] 已读 [DESIGN.md](../DESIGN.md)
- [ ] Prompt 使用 [PROMPT_TEMPLATES.md](PROMPT_TEMPLATES.md)
- [ ] 明确中文 UI 文案
- [ ] 明确 dark/light（本项目默认 **light**，桌面优先）
- [ ] 导出物写入 `exports/` / `screenshots/`
- [ ] 实现后 Playwright / chrome-devtools 验证
