# 设计输入层（DESIGN.md）

本目录是 **audiobook-cleaner-lab** 的 UI 设计输入层，供 Cursor / Codex / Agent 在实现页面前参考。

## 项目类型

**有声书音频清洗与文本对齐剪辑工具** — 原文 + ASR + LLM 机切建议 + 人工 Review + FFmpeg 导出。

核心 UI 场景：

- 项目 / 章节控制台
- **Review 审核台**（三栏文本 + 底栏波形，已实现 MVP）
- 批处理与导出状态
- Debug / 可观测性面板

## 设计来源优先级

1. [docs/UI_DESIGN.md](../UI_DESIGN.md) — 已实现页面的结构与交互约定
2. [docs/design/stitch/](stitch/) — Stitch 生成的原型、截图、HTML、DESIGN 变体
3. 当前 `apps/web/` 代码 — 落地实现以 React + Vite + TypeScript 为准

## Stitch 定位

- **负责**：UI 原型、设计系统草案、页面截图、HTML 参考、多方案 variants
- **不负责**：直接覆盖业务代码、替代主开发 Agent、自动提交未经审查的代码

## 技术栈约束

实现 UI 时必须遵守：

- 前端：React、Vite、TypeScript、wavesurfer.js
- 后端：FastAPI、本地 JSON + `data/`
- 中文 UI 文案
- 桌面优先（移动端后续）

## 状态色规范（与 UI_DESIGN 一致）

| 状态 | 颜色 |
|------|------|
| matched / keep | 绿 |
| delete 建议 | 红 |
| uncertain | 黄 |
| missing | 灰 |

## 导出物存放

| 类型 | 路径 |
|------|------|
| HTML / 设计稿导出 | `docs/design/stitch/exports/` |
| 截图 | `docs/design/stitch/screenshots/` |
| 审核记录 / 设计评审 | `docs/design/stitch/reviews/` |
| Prompt 存档 | `docs/design/stitch/prompts/` |

## Agent 工作流

1. 读本文档 + `docs/design/stitch/README.md`
2. 若 Stitch MCP 可用，用模板生成设计（见 `PROMPT_TEMPLATES.md`）
3. 将结果保存到上述目录
4. 拆成可落地任务后，在 `apps/web/` 实现
5. 用 **Playwright** 或 **chrome-devtools** 做浏览器验证

## 相关文档

- [stitch/README.md](stitch/README.md)
- [stitch/STITCH_WORKFLOW.md](stitch/STITCH_WORKFLOW.md)
- [stitch/UI_TASKS.md](stitch/UI_TASKS.md)
- [stitch/PROMPT_TEMPLATES.md](stitch/PROMPT_TEMPLATES.md)
