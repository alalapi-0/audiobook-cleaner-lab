# -*- coding: utf-8 -*-
"""Review API 路由。"""

from __future__ import annotations

from typing import Any

try:
    from fastapi import APIRouter, HTTPException
    from pydantic import BaseModel, Field
except ImportError:  # Round 06 前兼容：未安装 FastAPI 时不阻断仓库检查
    APIRouter = None  # type: ignore[misc, assignment]

    class BaseModel:  # type: ignore[no-redef]
        pass

    class HTTPException(Exception):  # type: ignore[no-redef]
        def __init__(self, status_code: int, detail: str) -> None:
            self.status_code = status_code
            self.detail = detail

    def Field(*args: Any, **kwargs: Any) -> Any:  # type: ignore[misc]
        return None


if APIRouter is not None:

    from apps.api.services.review_service import ReviewService

    router = APIRouter(prefix="/api", tags=["review"])
    review_service = ReviewService()

    class UserDecisionItem(BaseModel):
        """单 segment 用户决策。"""

        segment_id: str
        user_action: str = Field(..., pattern="^(keep|delete|uncertain)$")
        user_adjusted_cut: dict[str, float] | None = None
        note: str = ""

    class SaveReviewRequest(BaseModel):
        """保存 Review 请求体。"""

        decisions: list[UserDecisionItem]

    class UpdateCutPlanRequest(BaseModel):
        """更新 cut_plan 请求体。"""

        delete_ranges: list[dict[str, Any]]
        keep_ranges: list[dict[str, Any]] = Field(default_factory=list)
        version: int = 1

    @router.get("/health")
    def health() -> dict[str, str]:
        """健康检查。"""
        return {"status": "ok"}

    @router.get("/projects/{project_id}/chapters/{chapter_id}/review-data")
    def get_review_data(project_id: str, chapter_id: str) -> dict[str, Any]:
        """获取 Review 页面数据。"""
        try:
            return review_service.get_review_data(project_id, chapter_id)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @router.get("/projects/{project_id}/chapters/{chapter_id}/cut-plan")
    def get_cut_plan(project_id: str, chapter_id: str) -> dict[str, Any]:
        """获取 cut_plan。"""
        try:
            return review_service.get_cut_plan(project_id, chapter_id)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @router.put("/projects/{project_id}/chapters/{chapter_id}/cut-plan")
    def update_cut_plan(
        project_id: str,
        chapter_id: str,
        body: UpdateCutPlanRequest,
    ) -> dict[str, Any]:
        """更新 cut_plan（波形微调）。"""
        chapter = review_service.manifest_service.load_chapter(project_id, chapter_id)
        cut_plan = {
            "chapter_id": chapter_id,
            "source_audio": chapter.source_audio,
            "version": body.version,
            "delete_ranges": body.delete_ranges,
            "keep_ranges": body.keep_ranges,
            "export": {
                "format": "mp3",
                "bitrate": "192k",
                "output_path": chapter.artifacts.export,
            },
        }
        return review_service.update_cut_plan(project_id, chapter_id, cut_plan)

    @router.post("/projects/{project_id}/chapters/{chapter_id}/review")
    def save_review(
        project_id: str,
        chapter_id: str,
        body: SaveReviewRequest,
    ) -> dict[str, Any]:
        """保存 user_review 与 cut_plan。"""
        try:
            return review_service.save_review(
                project_id,
                chapter_id,
                [d.model_dump() for d in body.decisions],
            )
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

else:
    router = None  # type: ignore[assignment]
