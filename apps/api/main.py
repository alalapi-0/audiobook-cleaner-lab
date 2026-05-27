"""
audiobook-cleaner-lab FastAPI 后端

Round 06 起提供 Review API。未安装 FastAPI 时本模块仍可被 check_repo 引用。
"""

from __future__ import annotations

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware

    from apps.api.routes.review import router as review_router

    app = FastAPI(
        title="audiobook-cleaner-lab API",
        version="0.1.0",
        description="有声书清洗流水线 API — Review / 导出等",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(review_router)

except ImportError:
    app = None  # type: ignore[assignment]
