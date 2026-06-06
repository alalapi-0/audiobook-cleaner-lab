# Google Stitch — UI 设计能力

Stitch 是本项目的 **UI 设计输入工具**，通过 MCP 为 Agent 提供页面原型、设计系统、截图与 HTML 参考。

## 在本项目中的用途

- 生成 Review 审核台、项目控制台、Debug 面板等界面设计
- 输出 screen HTML、截图、DESIGN.md 变体
- 为 Cursor 实现 `apps/web/` 时提供视觉与布局参考

## 不应用于

- 替代主开发 Agent
- 无审查覆盖 `apps/web/` 或 `packages/` 业务代码
- 自动删除项目文件或未经审查提交大段生成代码
- 保存或暴露 API Key

## 快速配置

### 1. 设置 API Key

```bash
cp .env.example .env
# 编辑 .env，填入 STITCH_API_KEY（勿提交 .env）
```

或在 shell / Cursor 环境中：

```bash
export STITCH_API_KEY=your_key_here
```

### 2. 安装 proxy 依赖

```bash
npm install
```

### 3. 加载 MCP

配置已写入 [`.cursor/mcp.json`](../../../.cursor/mcp.json) 的 `stitch` server（本地 stdio proxy）。

修改后 **重启 Cursor 或 Reload Window**，在 **Settings → MCP** 确认 `stitch` 已启用。

### 4. 验证

```bash
npm run check:stitch
npm run check:mcp
```

若已设置 `STITCH_API_KEY`，可在 Cursor 中向 Agent 发起 Stitch 设计任务验证连通性。

## 文档索引

| 文档 | 内容 |
|------|------|
| [STITCH_MCP_SETUP.md](STITCH_MCP_SETUP.md) | MCP 配置详解（Remote vs Proxy） |
| [STITCH_WORKFLOW.md](STITCH_WORKFLOW.md) | 设计 → 实现 → 验证工作流 |
| [UI_TASKS.md](UI_TASKS.md) | 设计任务模板 |
| [PROMPT_TEMPLATES.md](PROMPT_TEMPLATES.md) | Stitch 专用 prompt |
| [EXPORT_GUIDE.md](EXPORT_GUIDE.md) | 导出 HTML / 截图规范 |

## 结果保存位置

- `exports/` — HTML、DESIGN.md 导出
- `screenshots/` — 页面截图
- `reviews/` — 设计评审记录
- `prompts/` — 使用过的 prompt 存档

## 安全

- **禁止**将真实 `STITCH_API_KEY` 写入仓库
- **禁止**在 `.cursor/mcp.json` 硬编码 key
- 使用环境变量 `${env:STITCH_API_KEY}` 映射

详见 [STITCH_MCP_SETUP.md](STITCH_MCP_SETUP.md)。
