# Stitch 导出指南

## 导出类型

| 类型 | 建议路径 | 用途 |
|------|----------|------|
| HTML screen | `exports/{page}-{date}.html` | 布局与结构参考 |
| DESIGN.md | `exports/{page}-DESIGN-{date}.md` | 设计决策文档 |
| Screenshot | `screenshots/{page}-{date}-v{n}.png` | 视觉评审 |
| Prompt 存档 | `prompts/{page}-{date}.md` | 可复现生成 |
| 评审记录 | `reviews/{page}-{date}.md` | 通过/修改意见 |

## 导出步骤（Agent）

1. 通过 Stitch MCP 获取 screen HTML 或截图
2. 将内容写入对应目录（**不要**写入 `apps/web/`）
3. 在 `reviews/` 记录：采纳项、待改项、与现有 UI 差异
4. 在实现 PR / round 报告中引用文件路径

## 与业务代码的关系

- `exports/` 中的 HTML **仅供参考**，需人工/Agent 审查后手工转写为 React 组件
- 不得 `cp` 或批量替换 `apps/web/src/`
- 状态色、文案以 [DESIGN.md](../DESIGN.md) 与 [UI_DESIGN.md](../../UI_DESIGN.md) 为准

## Git 策略

- 设计导出物（HTML、PNG、MD）**可以**进入 Git（体积小）
- **禁止**提交含 API Key 的文件
- 大体积截图考虑压缩或仅保留关键帧

## 示例评审模板（reviews/）

```markdown
# Review Workbench 设计评审 — 2026-06-06

## 来源
- Stitch screen: exports/review-workbench-20260606.html
- Screenshot: screenshots/review-workbench-20260606-v1.png

## 采纳
- 三栏 + 底栏波形布局
- uncertain 黄色高亮样式

## 待改
- 需对齐现有 WaveformEditor API
- 移动端暂不实现

## 实现任务
- [ ] 调整 ModelSuggestionPanel 间距
- [ ] 统一 status 色标与 DESIGN.md
```
