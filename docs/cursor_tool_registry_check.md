# Cursor Current Thread Tool Registry Check

本文档说明 **MCP server 在 CLI/Settings 层 ready** 与 **当前 Agent 对话线程实际暴露工具** 之间的差异，以及常见故障的排查与修复方式。

> 配套 Runbook：[cursor_browser_ui_runbook.md](cursor_browser_ui_runbook.md)

---

## 核心事实

### 1. 终端里的 MCP ready 只能说明 server 可用

`cursor-agent mcp list` 或 Settings 中绿色 ready 状态，表示 Cursor 进程**能够启动并连接**该 MCP server。这不等于当前正在运行的 Agent 对话已经拿到该 server 的工具描述符。

### 2. 当前 Agent 对话必须实际暴露工具

每个 Agent 对话线程在创建时会绑定一份 **工具注册表**。只有注册表中的工具才能被该对话调用。新批准的 MCP、修改后的 `.cursor/mcp.json`，**不会自动注入到已存在的对话**。

### 3. Multitask 子 Agent 可能没有继承 Workspace MCP

Multitask 模式下派生的后台子 Agent，历史上存在 **未继承 Workspace MCP 工具注册表** 的情况。因此浏览器控制任务在 Multitask 中经常报 `server does not exist` 或工具列表缺失。

**处理方式**：涉及 browser / chrome-devtools / playwright 的任务 **禁止使用 Multitask**，改用普通前台 Agent。

### 4. 旧对话可能仍停留在批准前的工具注册表

用户在 Settings 中批准 MCP 之前发起的对话，可能永久停留在「批准前」的工具集。即使后来 server 已 ready，该对话仍无法调用新工具。

### 5. 正确处理方式：完全重启 Cursor + 新建普通 Agent 对话

推荐修复步骤（按顺序）：

1. Settings → Tools & MCP → 确认目标 server 为 ready（必要时批准）。
2. **完全退出 Cursor**（不是仅关闭窗口或 Reload）。
3. 重新打开本仓库。
4. **新建**普通前台 Agent 对话（不要继续旧线程）。
5. **禁用 Multitask**。
6. 重新执行 UI 任务；任务开始前确认线程工具列表。

### 6. Server 名称连字符与路由问题

部分环境下，MCP server 名称中的连字符（如 `chrome-devtools`、`wechat-chrome-session`）可能导致工具路由异常。若文档或历史 issue 记录过此类问题，可在 `.cursor/mcp.json` 中增加 **underscore alias**（如 `chrome_devtools`），但必须在文档中说明 alias 与主名称的对应关系，且 **不覆盖** 已有主配置。

本仓库当前使用标准连字符名称，未配置 alias。若遇路由问题再按需添加。

---

## 排查表

| 现象 | 可能原因 | 解决方法 |
| --------------------------------------------------------- | ----------------------------------- | -------------------------------------------- |
| `cursor-agent mcp list` 显示 ready，但对话中 server does not exist | 当前线程未继承工具注册表 | 完全退出 Cursor，新建普通前台 Agent |
| Multitask 中缺少 MCP 工具 | 子 Agent 未继承 Workspace MCP | 禁用 Multitask，改用普通前台 Agent |
| `wechat-chrome-session` ready 但无法调用（其他项目） | 工具未暴露给当前线程或名称路由问题 | 新建前台 Agent；必要时增加 `wechat_chrome_session` alias |
| Playwright 打开的是未登录页面 | Playwright 新开隔离浏览器 | 微信任务改用 `wechat-chrome-session`；本地 Web 任务属正常行为 |
| chrome-devtools 不能接管现有页面 | Chrome 未开启 remote debugging 或线程没有工具 | 按 chrome-devtools MCP 文档启动 remote debugging；重启 Cursor 并新建对话 |
| stitch 工具列表为空 | `STITCH_API_KEY` 未设置或线程未刷新 | 设置环境变量 → `npm install` → 重启 Cursor → 新建对话 |
| github 工具不可用 | `GITHUB_TOKEN` 未设置 | 通过环境变量提供 token；不写入仓库 |
| 脚本 `check:cursor-mcp` 通过但对话仍失败 | 脚本仅检查 CLI 层 | 以当前对话线程工具列表为准，执行 BLOCKED 流程 |

---

## 检查命令

```bash
# CLI 层 MCP 列表与 list-tools（不代表当前对话线程）
bash scripts/check_cursor_mcp_status.sh
npm run check:cursor-mcp

# 仓库配置格式与安全（不含线程状态）
npm run check:mcp
npm run check:stitch
```

**重要**：`check_cursor_mcp_status.sh` 明确提示——该脚本只检查 CLI 层，**不代表**当前 Agent 对话线程已暴露工具。

---

## Agent 缺工具时的标准输出

```
BLOCKED: MISSING_FROM_THREAD_TOOL_REGISTRY

缺失：<tool/server 名称>

用户操作：
1. 完全退出 Cursor
2. 重新打开仓库
3. Settings → Tools & MCP 确认 ready
4. 新建普通前台 Agent 对话
5. 禁用 Multitask
6. 重新执行任务
```

Agent **不得**在 BLOCKED 状态下继续假装完成浏览器检查或 UI 验收。

---

## 本仓库 MCP 清单

| Server | 线程检查关注点 |
|--------|----------------|
| chrome-devtools | `take_screenshot`、`list_console_messages`、`list_network_requests` 等 |
| playwright | `browser_navigate`、`browser_snapshot` 等 |
| stitch | `generate_screen`、`list_projects` 等（视 proxy 暴露为准） |
| filesystem | 项目目录读写工具 |
| context7 | 文档查询工具 |
| github | 仓库/issue/PR 工具 |

本仓库 **不包含** `wechat-chrome-session`（非微信项目）。
