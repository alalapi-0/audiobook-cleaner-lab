#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""启动 FastAPI 开发服务器。"""

from __future__ import annotations

import sys


def main() -> int:
    """CLI 入口。"""
    try:
        import uvicorn
    except ImportError:
        print("错误: 请先安装依赖 pip install fastapi uvicorn", file=sys.stderr)
        return 1

    uvicorn.run(
        "apps.api.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
