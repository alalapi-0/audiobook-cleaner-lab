# Round 06 — 人工校正页面 MVP

**状态：已完成（2026-05-27）**

## Round 目标

网页查看原文、ASR、模型建议，支持确认/驳回/不确定，保存 `user_review.json` 与 `cut_plan.json`。

## 前置条件

Round 05 llm_cut_decision 可用。

## 主要任务

- Vite + React 项目初始化
- Review 三栏布局（见 `UI_DESIGN.md`）
- 后端 API 读取 JSON
- 保存 review 与 cut_plan

## 输出文件

- `apps/web/src/` Review 页面
- `apps/api/routes/review.py`

## 验收标准

- 本地打开页面完成 mock 章节 Review
- cut_plan 含 confirmed_by_user

## 不做什么

- 不做波形拖动（Round 07）

## 完成记录

- [x] `apps/api/services/review_service.py`
- [x] `apps/api/routes/review.py` — GET review-data / POST review
- [x] `apps/api/main.py` — FastAPI + CORS
- [x] `apps/web/` — Vite + React + TypeScript Review 三栏 MVP
- [x] `scripts/run_api.py`
- [x] `tests/test_review_api.py` — 3 项测试

## 本地启动

```bash
# 后端
python3 scripts/run_api.py   # 或 .venv/bin/python scripts/run_api.py

# 前端（需 npm install）
cd apps/web && npm install && npm run dev
# 打开 http://localhost:5173/?project_id=book_001&chapter_id=chapter_001
```

## 验收结果

```bash
python3 -m unittest tests.test_review_api -v  # 3 tests OK（需 fastapi + httpx）
python3 scripts/check_repo.py
```

## 下一轮衔接

Round 07：wavesurfer.js 波形编辑
