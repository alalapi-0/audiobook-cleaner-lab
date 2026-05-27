"""
audiobook-cleaner-lab API 占位模块

Round 00 说明：
- 本文件仅为 FastAPI 后端占位，不强制安装 FastAPI 即可通过仓库检查。
- 后续 Round 将逐步引入真实路由与服务。

未来 API 路由规划（草案）：
- GET  /health              — 健康检查
- POST /projects            — 创建书籍项目
- GET  /projects/{id}       — 获取项目 manifest
- POST /chapters/{id}/asr   — 触发 ASR（mock/真实 Adapter）
- POST /chapters/{id}/align — 生成 alignment.json
- POST /chapters/{id}/llm-cut — 生成 llm_cut_decision.json
- GET  /chapters/{id}/review — 获取 review 数据
- POST /chapters/{id}/cut-plan — 保存 cut_plan.json
- POST /chapters/{id}/export — FFmpeg 导出

当前默认假设：单用户本地运行，SQLite 持久化（Round 01 起设计）。
"""

# Round 00：不导入 FastAPI，避免未安装依赖导致检查失败
