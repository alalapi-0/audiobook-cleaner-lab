# Round 11 — 本地运行与使用体验

**状态：已完成（2026-05-27）**

## Round 目标

一键启动 API + Web、环境检查、README 完整教程。

## 前置条件

Round 01–10 核心能力就绪。

## 主要任务

- `scripts/start_local.sh`（或 .py）
- `scripts/check_environment.py`（Python、FFmpeg、Node）
- 完善 README 端到端教程
- 可选：docker-compose 草案

## 输出文件

- 启动脚本
- 更新 README、PROJECT_STATE

## 验收标准

- 新用户按 README 完成 mock 单章全流程
- 环境检查脚本中文输出

## 不做什么

- 不做云部署与安装包

## 完成记录

- [x] `scripts/check_environment.py`
- [x] `scripts/start_local.sh`
- [x] README 端到端教程更新

## 验收结果

```bash
python3 scripts/check_environment.py
bash scripts/start_local.sh   # 需 Node.js
```

## 下一轮衔接

项目进入维护迭代；新需求开 Stage 12+。
