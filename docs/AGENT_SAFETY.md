# Agent 安全规则（Safety）

## 默认禁止

- 读取/提交 `.env`、API Key、Token
- 真实付费 ASR/LLM（gate/探针默认）
- 真实内容发布到外部平台
- 覆盖 `data/` 原始音频
- `git push --force` main
- 打印密钥到日志或报告
- 提交大文件、浏览器 session、真实用户数据

## 开关

| 开关 | 位置 | 默认 |
|------|------|------|
| allow_real_api | `agent_layer.yaml` | false |
| allow_real_publish | `agent_layer.yaml` | false |
| LLM_API_KEY | `.env`（不进 Git） | 未配置 |

## 真实 API 流程

仅当用户显式配置且遵循 `docs/testing/REAL_API_TESTING.md`：

1. 复制 `.env.example` → `.env`（本地）
2. `python3 scripts/real_api_check.py`
3. 记录到 `reports/real_api_runs/`
4. **不**纳入默认 `agent_gate.py` 硬失败

## MCP 安全

- GitHub token 仅环境变量
- filesystem 仅 `${workspaceFolder}`
- Stitch key 不进仓库
- 探针禁止调用写操作 MCP 方法

## 误触发恢复

- 导出始终支持 `--dry-run`
- batch 支持 `--skip-export`
- 切点存 JSON，不破坏原 wav
