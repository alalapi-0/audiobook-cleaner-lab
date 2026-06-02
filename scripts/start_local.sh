#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# 本地一键启动 API + Web 开发服务器

set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "======================================"
echo "audiobook-cleaner-lab 本地启动"
echo "======================================"

# 环境检查
python3 scripts/check_environment.py || true

if [ -d ".venv" ]; then
  PY=".venv/bin/python"
else
  PY="python3"
fi

# 初始化 data 目录
$PY scripts/init_data_dirs.py

# 演示章节（Review 主链路依赖，仅写入 data/）
DEMO_MANIFEST="data/projects/book_001/chapters/chapter_001/chapter_manifest.json"
if [ ! -f "$DEMO_MANIFEST" ]; then
  echo ""
  echo "生成演示章节 mock 数据 (book_001/chapter_001) ..."
  $PY scripts/seed_demo_chapter.py
fi

# 启动 API（后台）

echo ""
echo "启动 API (http://127.0.0.1:8000) ..."
$PY -m uvicorn apps.api.main:app --host 127.0.0.1 --port 8000 --reload &
API_PID=$!

cleanup() {
  echo ""
  echo "停止 API (pid $API_PID)..."
  kill "$API_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# 启动前端
if command -v npm >/dev/null 2>&1 && [ -f "apps/web/package.json" ]; then
  echo "启动 Web (http://127.0.0.1:5173) ..."
  cd apps/web
  if [ ! -d "node_modules" ]; then
    echo "首次运行，正在 npm install..."
    npm install
  fi
  npm run dev
else
  echo "Node.js 未安装，仅 API 运行中。Ctrl+C 退出。"
  wait "$API_PID"
fi
