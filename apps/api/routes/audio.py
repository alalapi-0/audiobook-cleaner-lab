# -*- coding: utf-8 -*-
"""音频文件只读访问路由。"""

from __future__ import annotations

from pathlib import Path

try:
    from fastapi import APIRouter, HTTPException
    from fastapi.responses import FileResponse
except ImportError:
    APIRouter = None  # type: ignore[misc, assignment]

ROOT = Path(__file__).resolve().parents[3]
ALLOWED_PREFIXES = ("data/raw_audio/", "data/exports/")


if APIRouter is not None:
    router = APIRouter(prefix="/api/audio", tags=["audio"])

    @router.get("/{file_path:path}")
    def serve_audio(file_path: str) -> FileResponse:
        """只读提供 data/raw_audio 或 data/exports 下音频。"""
        normalized = file_path.replace("\\", "/")
        if not any(normalized.startswith(p) for p in ALLOWED_PREFIXES):
            raise HTTPException(status_code=403, detail="不允许访问该路径")

        full = ROOT / normalized
        if not full.is_file():
            raise HTTPException(status_code=404, detail="音频不存在")

        media = "audio/wav" if full.suffix.lower() == ".wav" else "audio/mpeg"
        return FileResponse(full, media_type=media)
else:
    router = None  # type: ignore[assignment]
