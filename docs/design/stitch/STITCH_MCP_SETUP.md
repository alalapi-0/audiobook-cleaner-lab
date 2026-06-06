# Stitch MCP 配置说明

## 当前方案：本地 stdio Proxy（推荐）

本仓库采用 **本地 proxy**，与现有 playwright / github 等 stdio MCP 保持一致，并安全支持环境变量。

### 配置位置

[`.cursor/mcp.json`](../../../.cursor/mcp.json)：

```json
"stitch": {
  "type": "stdio",
  "command": "node",
  "args": ["scripts/stitch_mcp_proxy.mjs"],
  "env": {
    "STITCH_API_KEY": "${env:STITCH_API_KEY}"
  }
}
```

### Proxy 脚本

[`scripts/stitch_mcp_proxy.mjs`](../../../scripts/stitch_mcp_proxy.mjs) 使用官方 `@google/stitch-sdk` 的 `StitchProxy`：

- 从 `STITCH_API_KEY` 读取密钥
- 缺失时输出明确错误并退出
- **不打印** key

### 依赖

根目录 `package.json` devDependencies：

- `@google/stitch-sdk`
- `@modelcontextprotocol/sdk`

安装：`npm install`

## 备选：Remote MCP（未默认启用）

Stitch 官方 Remote endpoint：

```text
https://stitch.googleapis.com/mcp
```

认证 header：

```text
X-Goog-Api-Key: <STITCH_API_KEY>
```

**未采用为默认方案的原因**：Cursor Remote MCP 的 header 环境变量插值支持因版本而异；硬编码 key 违反安全规则。若未来 Cursor 稳定支持 header 中的 `${env:STITCH_API_KEY}`，可切换为：

```json
"stitch": {
  "type": "http",
  "url": "https://stitch.googleapis.com/mcp",
  "headers": {
    "X-Goog-Api-Key": "${env:STITCH_API_KEY}"
  }
}
```

切换前请在本机验证 MCP 面板可连接，并运行 `npm run check:stitch`。

## 环境变量

| 变量 | 必需 | 说明 |
|------|------|------|
| `STITCH_API_KEY` | 是（使用 Stitch 时） | Google Stitch API Key |

示例见 [`.env.example`](../../../.env.example)。

## 加载与验证步骤

1. `cp .env.example .env` 并填入 `STITCH_API_KEY`
2. `npm install`
3. `npm run check:stitch`
4. 重启 Cursor → Settings → MCP → 确认 `stitch` enabled
5. 在 Agent 对话中请求生成简单 Dashboard 原型测试

## 故障排查

| 现象 | 处理 |
|------|------|
| `STITCH_API_KEY is not set` | 设置环境变量或 `.env`（Cursor 需能读取 env） |
| stitch server 红色 / 未连接 | 检查 `npm install`、Node ≥ 18、重启 Cursor |
| 工具调用超时 | 检查网络；Stitch 生成可能较慢 |
| 无 stitch 工具列表 | 确认 MCP 面板中 server 名称 exactly `stitch` |

## 安全检查

```bash
npm run check:stitch
npm run check:mcp
git diff   # 提交前确认无 key 泄露
```
