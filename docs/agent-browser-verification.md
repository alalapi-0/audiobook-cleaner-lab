# Agent 浏览器调试与验证闭环

本文档说明本仓库为 Cursor Agent 配置的浏览器调试、MCP 工具与自动化验证入口。

## 新增 MCP 服务器

以下 MCP 已写入 `.cursor/mcp.json`（合并模式，不覆盖已有同名配置）：

| MCP | 用途 |
|-----|------|
| **playwright** | 浏览器自动化：打开页面、点击、输入、截图、基础交互验证 |
| **chrome-devtools** | 深层 DevTools 调试：console、network、performance、DOM 检查 |
| **context7** | 查询最新库/框架文档（prompt 中可写 `use context7`） |
| **filesystem** | 读写当前项目目录（`${workspaceFolder}`），确认真实文件状态 |
| **github** | 读取仓库、issue、PR、提交状态（需环境变量 `GITHUB_TOKEN`） |
| **stitch** | UI 设计、原型、截图（需 `STITCH_API_KEY`，本地 proxy） |

多数 server 为 `npx` stdio；**stitch** 为 `node scripts/stitch_mcp_proxy.mjs`。**GitHub** 通过 `GITHUB_TOKEN` 映射；**Stitch** 通过 `STITCH_API_KEY`。勿在仓库中写死 token。详见 [docs/agent_skills/mcp_usage_skill.md](agent_skills/mcp_usage_skill.md) 与 [docs/design/stitch/STITCH_MCP_SETUP.md](design/stitch/STITCH_MCP_SETUP.md)。

## 在 Cursor 中确认 MCP 已启用

1. **重启 Cursor**（修改 `.cursor/mcp.json` 后必须重启）
2. 打开 **Cursor Settings → Tools & MCP**（或 **MCP**）
3. 确认以下 server 状态为可用（绿色/已连接）：
   - `playwright`
   - `chrome-devtools`
   - `context7`
   - `filesystem`
   - `github`（需本地配置 `GITHUB_TOKEN`）
   - `stitch`（需 `STITCH_API_KEY` 与 `npm install`）
4. 若某 server 报错，查看 Output 面板中的 MCP 日志；常见原因是 Node 未安装或网络无法拉取 `npx` 包

## Skill 与 Rule

| 文件 | 作用 |
|------|------|
| `.cursor/skills/browser-debug-check/SKILL.md` | 浏览器级验证闭环技能（console/network/用户路径/验证报告） |
| `.cursor/rules/verification-gate.mdc` | 全局规则：涉及前端/UI/API 的任务必须走验证门禁 |
| `.cursor/rules/mcp-agent-tools.mdc` | MCP 安全与授权约束 |
| `docs/agent_skills/mcp_usage_skill.md` | MCP 用途、降级策略与自动推进用法 |

## 验证命令

根目录 `package.json` 与 `scripts/agent_gate.py`：

```bash
python3 scripts/agent_gate.py   # 仓库骨架 + 环境 + compileall + npm run agent:check
python3 scripts/check_mcp_config.py  # MCP 配置格式与安全检查
npm run check:mcp               # 同上
python3 scripts/seed_demo_chapter.py  # 本地 Review 演示数据（写入 data/，不进 Git）
npm run agent:check   # 组合 build + test（按项目现有 scripts 动态组合）
npm run test          # Playwright smoke test（apps/web，自动启动 Vite dev server）
npm run build         # 前端 TypeScript + Vite 构建
```

前端 Playwright 配置位于 `apps/web/playwright.config.ts`，smoke 测试位于 `apps/web/tests/smoke.spec.ts`。

**Smoke test 说明：**

- Playwright 会通过 `webServer` 自动启动 Vite dev server（`http://localhost:5173`；勿用 `127.0.0.1`，因 Vite 默认仅监听 `localhost`）
- 未启动 FastAPI 后端时，`/api` 代理会返回 500；smoke 测试会过滤此类预期网络错误，仅断言页面壳与无 JS 运行时 error
- 完整 API 集成验证需另行启动后端并配合 `/browser-debug-check` 技能

## Prompt 示例

**完整浏览器验证闭环：**

```
请调用 /browser-debug-check 技能完成本轮验证
```

**查最新框架文档：**

```
use context7 查询 Vite / React 最新文档，确认当前用法是否正确
```

**修改 Review 页后的典型流程：**

```
1. 启动 npm run dev
2. 用 Playwright MCP 或 Chrome DevTools MCP 打开 http://127.0.0.1:5173
3. 检查 console 与 network
4. 运行 npm run agent:check
5. 输出验证报告
```

## 安全注意事项

- **不要**让 MCP 打开真实支付后台或生产管理后台
- **不要**让 MCP 操作生产账号或真实用户数据
- **不要**把 API Key、token、cookie、session 写入仓库或 MCP 配置
- 测试文件删除/移动功能时，仅使用 `data/` 下的测试目录或 mock 数据
- smoke test 仅访问本地 dev server，不访问外网生产环境

## 相关文件清单

- `.cursor/mcp.json`
- `.cursor/skills/browser-debug-check/SKILL.md`
- `.cursor/rules/verification-gate.mdc`
- `.cursor/rules/mcp-agent-tools.mdc`
- `docs/agent_skills/mcp_usage_skill.md`
- `apps/web/playwright.config.ts`
- `apps/web/tests/smoke.spec.ts`
- `scripts/agent_gate.py`
- `scripts/seed_demo_chapter.py`
- 根目录 `package.json` 中的 `agent:check` / `test` scripts
