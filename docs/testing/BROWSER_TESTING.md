# 浏览器测试说明

## 适用范围

- Review 审核台（`apps/web/`）
- 任何涉及页面、审核工作台、文件上传 UI 的改动

## 工具

| 工具 | 用途 |
|------|------|
| **Playwright MCP** | 自动化打开页面、点击、输入、截图 |
| **chrome-devtools MCP** | console、network、DOM、性能 |
| **apps/web Playwright** | CI 式 smoke：`npm run test` |

## 默认地址

- 前端：`http://localhost:5173`（Vite；勿用 `127.0.0.1` 若仅监听 localhost）
- API：`http://127.0.0.1:8000`
- Review 示例：`http://localhost:5173/?project_id=book_001&chapter_id=chapter_001`（`127.0.0.1:5173` 亦可）

## 启动方式

```bash
bash scripts/start_local.sh   # API + Web + 自动 seed
# 或
python3 scripts/run_api.py &
npm run dev
python3 scripts/seed_demo_chapter.py
```

## 验证清单

- [ ] 页面正常渲染，无白屏
- [ ] console 无未解释 error
- [ ] network：核心 API 非 5xx（允许 mock 路径）
- [ ] 核心用户路径可走通（加载 → 交互 → 保存/反馈）
- [ ] 波形、segment 联动等基本行为

## 命令

```bash
npm run test              # Playwright smoke
npm run agent:check       # build + test
python3 scripts/agent_gate.py
```

## 相关文档

- [agent-browser-verification.md](../agent-browser-verification.md)
- [.cursor/skills/browser-debug-check/SKILL.md](../../.cursor/skills/browser-debug-check/SKILL.md)
- [USER_PERSPECTIVE_TESTING.md](USER_PERSPECTIVE_TESTING.md)
