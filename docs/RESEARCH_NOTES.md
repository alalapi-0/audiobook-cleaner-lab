# Research Notes

Date: 2026-06-09  
Agent: Cursor  
Search capability: available

## Query 1 — Cursor Agent 定制能力（Rules / Skills / MCP）

- Query: Cursor IDE Agent Rules Skills MCP Plugins 2026 official
- Source type: official docs + official blog
- Key finding: Cursor 通过 `.cursor/rules/` 提供静态规则；Skills 为 `SKILL.md` 动态加载；MCP 在 `mcp.json` 配置；CLI 工具（gh/docker）可直接由 Agent 调用；Plugins 可打包 rules/skills/MCP。
- Relevance to this repo: 已对齐 `.cursor/rules/`、`.cursor/skills/`、`.cursor/mcp.json`；新增 agent-layer 规则层。
- Risk / uncertainty: Skills 部分能力可能依赖 Cursor Nightly/Beta 频道；需用户确认版本。
- Action to encode into repo: `docs/TOOL_INVENTORY.md`, `.cursor/rules/agent-layer.mdc`, `docs/RESEARCH_NOTES.md`

## Query 2 — Codex CLI / AGENTS.md / MCP / Subagents

- Query: OpenAI Codex CLI AGENTS.md MCP web search subagents 2026
- Source type: official docs (developers.openai.com)
- Key finding: Codex 分层读取 AGENTS.md（全局→项目根→当前目录）；支持 MCP（`config.toml`）、Subagents、Web Search、`exec` 脚本化；与 Skills、Memories 互补。
- Relevance to this repo: `AGENTS.md` 补强为跨 Agent 入口；`docs/CODEX_USAGE.md` / `CODEX_HANDOFF.md` 供未来 Codex 介入。
- Risk / uncertainty: Codex 本机 CLI 未在本轮 shell 探针中验证安装；记为 `CODEX_AVAILABLE: manual`。
- Action to encode into repo: `docs/CODEX_USAGE.md`, `agent_tools.yaml` codex surface

## Query 3 — 本项目技术栈（未单独搜索，使用已知官方源）

- Query: FastAPI / React / Vite / Playwright / FFmpeg 最新文档
- Source type: official docs（索引见 `docs/SEARCH_POLICY.md`）
- Key finding: 本项目栈稳定；遇版本冲突时用 context7 或 WebSearch 查具体 API。
- Relevance to this repo: audio pipeline + Review UI；Playwright 已用于 E2E。
- Risk / uncertainty: Python 3.14 较新，部分依赖未在 CI 广泛验证。
- Action to encode into repo: `docs/SEARCH_POLICY.md` 技术栈索引

## Query 4 — 平台发布 / 真实 API

- Query: （本仓库当前无开放发布 API）
- Source type: internal repo policy
- Key finding: 默认 mock ASR/LLM；真实 API 需 `.env` Key；无自动发布到社交平台。
- Relevance: `agent_layer.yaml` `allow_real_api: false`
- Risk: 用户配置 Key 后须走 `real_api_check.py` 与 `docs/testing/REAL_API_TESTING.md`
- Action: `docs/AGENT_SAFETY.md`, `docs/COST_CONTROL.md`
