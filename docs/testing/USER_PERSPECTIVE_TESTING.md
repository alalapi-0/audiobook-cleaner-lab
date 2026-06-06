# 用户视角测试说明

## 角色分工

| Agent | 角色 |
|-------|------|
| **Codex** | 用户视角测试：发现问题、输出改进任务，**不直接修代码** |
| **Cursor** | 推进 Agent：根据测试任务落地修复 |
| **Stitch** | 设计输入（可选）：提供 UI 原型参考 |

## Codex 测试范围

- 以真实用户路径操作 Review 页
- 检查文案、布局、交互是否符合 [UI_DESIGN.md](../UI_DESIGN.md)
- 记录 console / network 问题
- 区分 mock 与 real_api 场景下的预期差异

## 测试必须通过

1. **浏览器**：Playwright 或真实浏览器打开本地 dev server
2. **API 路径**：需要时启动 FastAPI + seed 数据
3. **不可**仅凭静态代码阅读宣布通过

## 输出格式（Codex）

```markdown
## 用户视角测试报告

### 通过项
- ...

### 问题
1. [严重] ...
2. [一般] ...

### 改进任务（给 Cursor）
- [ ] 任务描述 + 复现步骤 + 期望行为
```

## Cursor 修复后

- 重新跑 `npm run agent:check` 或 `agent_gate.py`
- Playwright / chrome-devtools 回归
- 可选：更新 `docs/design/stitch/reviews/` 若涉及 UI 变更

## 相关命令

```bash
bash scripts/start_local.sh
npm run test
python3 scripts/agent_gate.py
```
