# MCP 故障排查指南

## 快速诊断

```bash
npm run check:mcp          # 仓库配置层检查
npm run check:stitch       # stitch 专项
npm run check:cursor-mcp   # CLI 层状态（不代表当前对话线程）
node scripts/print_mcp_manual_steps.js
```

`check:mcp` 通过只说明 **仓库配置文件合法**，不代表当前 Agent 线程已加载 MCP。

---

## 常见问题

### CLI 显示 server 存在，但当前线程不可用

**原因：** MCP 已在 Cursor 配置中注册，但未注入到**当前 Agent 对话线程**。

**处理：**

1. Settings → Tools & MCP → 确认 server 已批准且为绿色/已连接
2. 完全退出 Cursor → 重开仓库
3. **新建**普通前台 Agent 对话（不要用旧对话、不要用 Multitask）
4. 在新对话中验证工具列表

---

### ListMcpResources 返回空 / No MCP resources found

**原因：** 多数 MCP server 不提供 Resource 端点；或 server 未加载到当前线程。

**处理：**

- 空 resources **不一定**表示 MCP 失败——应检查 **Tools** 是否可用
- 若 Tools 也不可用，按「needs approval / 重启 / 新对话」流程处理

---

### Server 显示 not loaded / needs approval

**原因：** 用户尚未在 Cursor UI 中批准该 MCP server。

**处理：**

1. Cursor Settings → Tools & MCP
2. 找到对应 server → 点击批准/启用
3. 完全退出 Cursor 并重启
4. 新建 Agent 对话

---

### 配置改了但工具没有出现

**检查清单：**

| 步骤 | 说明 |
|------|------|
| JSON 合法 | `npm run check:mcp` |
| 已批准 | Settings → Tools & MCP |
| 已重启 | 完全退出 Cursor，非仅关窗口 |
| 新对话 | 旧线程不会自动更新工具 |
| 非 Multitask | 浏览器相关 MCP 在 Multitask 中常不可用 |
| Node 可用 | stitch 需要 `node`；npx server 需要网络 |

---

### GitHub token 缺失

**现象：** github server 红色、连接失败、401 错误。

**处理：**

1. 在 shell 或 Cursor 环境中设置 `GITHUB_TOKEN` 或 `GITHUB_PERSONAL_ACCESS_TOKEN`
2. 参考 [`.env.example`](../.env.example)：`cp .env.example .env` 后填入（勿提交 `.env`）
3. 重启 Cursor
4. 无 token 时 Agent 应降级为 `git` / `gh` CLI，不阻塞其他 MCP

---

### Stitch API Key 缺失

**现象：** `STITCH_API_KEY is not set`；stitch server 无法启动。

**处理：**

1. 设置 `STITCH_API_KEY` 环境变量
2. `npm install`（确保 `@google/stitch-sdk` 已安装）
3. `npm run check:stitch`
4. 重启 Cursor 并新建对话
5. 无 key 时可用 `docs/design/stitch/UI_TASKS.md` 手动推进，不阻塞其他 MCP

---

### filesystem 允许目录错误

**现象：** filesystem 无法读写预期文件；或安全检查失败。

**本仓库策略：** 使用 `${workspaceFolder}`，Cursor 自动解析为当前仓库根。

**禁止：**

- 授权 `/` 或整个用户主目录 `~`
- 硬编码其他机器上的绝对路径后直接复制到新仓库

**修复：** 确保 mcp.json 中 filesystem args 含 `${workspaceFolder}`；运行 `npm run check:mcp`。

---

### playwright / chrome-devtools 冲突

**现象：** 两个浏览器 MCP 同时操作导致 profile 占用、端口冲突、页面状态混乱。

**建议：**

- UI 验收优先选一个为主（playwright 做 E2E，chrome-devtools 做 console/network 深度调试）
- 关闭多余浏览器实例
- playwright 本仓库使用 `--isolated` 模式减少 profile 冲突
- 清理 `.playwright-mcp/` 缓存（已在 `.gitignore`）

---

### 浏览器 profile 被占用

**现象：** playwright 或 chrome-devtools 启动失败，提示 profile 锁定。

**处理：**

1. 关闭所有由 MCP 打开的 Chrome/Chromium 实例
2. 删除或清空 `.playwright-mcp/`（若存在）
3. 重启 Cursor
4. 避免 Multitask 中并行启动多个浏览器 MCP

---

### 当前线程没有专用工具

**结论：** 这是 **线程注册** 问题，不是仓库配置必然错误。

**必须：**

- 新建普通前台 Agent 对话
- 禁用 Multitask 测试浏览器 MCP
- 若仍无工具，输出 `BLOCKED: MISSING_FROM_THREAD_TOOL_REGISTRY` 并完全退出 Cursor 后重试

详见 [docs/cursor_tool_registry_check.md](cursor_tool_registry_check.md)。

---

### 为什么不能靠仓库文件直接让当前线程生效？

| 环节 | 说明 |
|------|------|
| 配置写入 | `.cursor/mcp.json` 仅告诉 Cursor **如何启动** server |
| 用户批准 | Cursor 安全模型要求 UI 层批准 |
| 进程启动 | stdio 子进程在 Cursor 启动/重载时 spawn |
| 工具注册 | 工具列表绑定到**新创建的** Agent 线程 |
| Token | 运行时从环境读取，不在 JSON 中硬编码 |

因此：**本轮治理完成 ≠ 当前对话立即可用 MCP**。

---

## 降级策略

MCP 不可用时 Agent 应继续推进并记录原因，见 [docs/agent_skills/mcp_usage_skill.md](agent_skills/mcp_usage_skill.md)。

| MCP 不可用 | 降级 |
|------------|------|
| github | `git` / `gh` CLI |
| playwright / chrome-devtools | `npm run test`、内置读文件 |
| filesystem | Cursor 内置 Read/Write 工具 |
| context7 | 项目内 docs、官方文档链接 |
| stitch | `docs/design/stitch/` 模板 |

---

## 进一步参考

- [MCP_SETUP.md](MCP_SETUP.md)
- [MCP_AUDIT.md](MCP_AUDIT.md)
- [docs/cursor_browser_ui_runbook.md](cursor_browser_ui_runbook.md)
