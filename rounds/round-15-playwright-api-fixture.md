# Round 15 — Playwright API Fixture

## 目标

Playwright 冒烟测试期间自动启动 FastAPI 并 seed 演示数据，消除 review-data 代理 ECONNREFUSED。

## 状态

**已完成**

## 本轮做了什么

1. `apps/web/playwright.config.ts` — 双 `webServer`（API 8000 + Vite 5173）
2. `WaveformEditor` — 波形未 ready 时禁用播放按钮，避免未初始化报错

## 验收

```bash
cd apps/web && npm run test
```

无 `ECONNREFUSED 127.0.0.1:8000` 代理错误。

## 下一轮

Round 13 R2 真实 LLM（需用户 API Key）。
