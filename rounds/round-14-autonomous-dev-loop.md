# Round 14 — Autonomous Dev Loop

## 目标

在无真实 LLM API Key 时仍能跑通「门禁 → mock 演示数据 → 本地 Review 主链路」，并为连续自动推进 Agent 提供统一入口。

## 状态

**已完成**

## 本轮做了什么

1. `scripts/auto_advance.py` — `init_data_dirs` + 按需 `seed_demo_chapter` + `agent_gate`
2. `scripts/start_local.sh` — 启动前自动 seed 演示章节（manifest 缺失时）
3. `check_repo.py` — 校验 round-12 / 13 / 14 文档
4. 根 `package.json` — `agent:advance` 脚本别名

## 验收

```bash
.venv/bin/python scripts/auto_advance.py --round 1
bash scripts/start_local.sh   # 另开终端
curl -s http://127.0.0.1:8000/api/projects/book_001/chapters/chapter_001/review-data | head
```

浏览器：Review 页加载 segments、无 console error、review-data 200。

## 不做什么

- 不调用真实付费 LLM（见 Round 13）
- 不提交 `data/` 真实内容

## 下一轮

Round 13 R2：用户配置 `LLM_API_KEY` 后运行 `real_api_check.py --pipeline`。
