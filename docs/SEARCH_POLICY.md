# 搜索策略（Search Policy）

Date: 2026-06-09  
记录位置: `docs/RESEARCH_NOTES.md`

## 必须搜索的情况

1. Cursor / Codex / MCP / Playwright / Browser / Chrome DevTools / GitHub CLI **能力变更**
2. 第三方库 API、框架配置、**版本差异**（React、Vite、FastAPI、Playwright、wavesurfer、FFmpeg）
3. 平台发布规则（若未来接入发布）
4. 微信公众号、短视频等外部平台限制（本仓库当前不涉及发布）
5. AI 模型 API、价格、参数、调用限制（ASR/LLM Adapter 接入时）
6. 安全、合规、支付规则
7. 报错无法仅凭本地代码判断
8. 用户明确要求「查一下」「搜索」「最新」

## 优先来源（从高到低）

1. 官方文档（cursor.com/docs, developers.openai.com/codex）
2. 官方 changelog / release notes
3. 官方 GitHub 仓库
4. 标准文档（JSON Schema、MCP 规范）
5. 高质量技术博客 / 论文
6. 社区讨论 — **仅辅助，不可当官方规则**

## 搜索结果处理

- 写入 `docs/RESEARCH_NOTES.md`（日期、关键词、来源类型、不确定性）
- 官方与博客冲突 → **以官方为准**
- 无法搜索 → 记录 `TOOL_UNAVAILABLE_WEB_SEARCH`，不编造 API

## 本仓库技术栈搜索索引

| 领域 | 建议官方入口 |
|------|----------------|
| Cursor Agent | https://cursor.com/docs |
| Codex | https://developers.openai.com/codex |
| FastAPI | https://fastapi.tiangolo.com |
| React / Vite | https://react.dev / https://vite.dev |
| Playwright | https://playwright.dev |
| wavesurfer.js | https://wavesurfer.xyz |
| FFmpeg | https://ffmpeg.org/documentation.html |
| MCP | https://modelcontextprotocol.io |

## Agent 行为

- `agent_layer.yaml`: `require_web_search_for_fresh_info: true`
- 搜索后把可执行结论编码进 `AGENTS.md` / runbook / 代码注释（仅非显而易见时）
- gate 脚本内 **不** 自动 Web 搜索
