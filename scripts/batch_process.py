#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""多章节批处理 CLI — 顺序执行 Round 02–09 流水线。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.api.services.manifest_service import ManifestService  # noqa: E402
from apps.api.services.review_service import ReviewService  # noqa: E402
from packages.alignment_core.service import AlignmentService  # noqa: E402
from packages.asr_core.adapters import MockAsrAdapter  # noqa: E402
from packages.asr_core.service import AsrService  # noqa: E402
from packages.audio_core.export_service import ExportService  # noqa: E402
from packages.feedback_core.service import FeedbackService  # noqa: E402
from packages.llm_core.service import LlmCutService  # noqa: E402
from packages.text_core.service import TextNormalizationService  # noqa: E402


def process_chapter(
    project_id: str,
    chapter_id: str,
    root: Path,
    skip_export: bool,
    auto_review: bool,
) -> list[str]:
    """处理单章节，返回日志行。"""
    logs: list[str] = []
    asr = AsrService(root=root)
    norm = TextNormalizationService(root=root)
    align = AlignmentService(root=root)
    llm = LlmCutService(root=root)
    review = ReviewService(root=root)
    export = ExportService(root=root)
    feedback = FeedbackService(root=root)

    steps = [
        ("asr", lambda: asr.run_asr(project_id, chapter_id, MockAsrAdapter())),
        ("normalize", lambda: norm.normalize_chapter(project_id, chapter_id)),
        ("align", lambda: align.align_chapter(project_id, chapter_id)),
        ("llm_cut", lambda: llm.run_llm_cut(project_id, chapter_id)),
    ]

    for name, fn in steps:
        try:
            fn()
            logs.append(f"  ✓ {chapter_id}: {name}")
        except Exception as exc:
            logs.append(f"  ✗ {chapter_id}: {name} 失败 — {exc}")
            return logs

    if auto_review:
        try:
            data = review.get_review_data(project_id, chapter_id)
            decisions = [
                {
                    "segment_id": s["segment_id"],
                    "user_action": s.get("model_action", "keep"),
                    "user_adjusted_cut": s.get("suggested_cut"),
                }
                for s in data["segments"]
            ]
            review.save_review(project_id, chapter_id, decisions)
            logs.append(f"  ✓ {chapter_id}: auto_review")
        except Exception as exc:
            logs.append(f"  ✗ {chapter_id}: auto_review 失败 — {exc}")
            return logs

    if not skip_export:
        try:
            export.export_chapter(project_id, chapter_id, dry_run=True)
            logs.append(f"  ✓ {chapter_id}: export dry-run")
        except Exception as exc:
            logs.append(f"  ✗ {chapter_id}: export 失败 — {exc}")

    try:
        feedback.generate_feedback(project_id, chapter_id)
        logs.append(f"  ✓ {chapter_id}: feedback")
    except Exception as exc:
        logs.append(f"  ⚠ {chapter_id}: feedback 跳过 — {exc}")

    return logs


def main() -> int:
    """CLI 入口。"""
    parser = argparse.ArgumentParser(description="audiobook-cleaner-lab 批处理")
    parser.add_argument("--project-id", required=True)
    parser.add_argument(
        "--chapter-ids",
        nargs="*",
        help="指定章节 ID，默认处理项目全部章节",
    )
    parser.add_argument("--skip-export", action="store_true")
    parser.add_argument(
        "--auto-review",
        action="store_true",
        help="自动采纳 model 建议作为 user_review（mock 测试用）",
    )
    args = parser.parse_args()

    manifest = ManifestService()
    project = manifest.load_project(args.project_id)
    chapter_ids = args.chapter_ids or [c.chapter_id for c in project.chapters]

    if not chapter_ids:
        print("错误: 无章节可处理", file=sys.stderr)
        return 1

    print(f"批处理开始: {args.project_id}，共 {len(chapter_ids)} 章\n")
    failed = 0
    for cid in chapter_ids:
        logs = process_chapter(
            args.project_id,
            cid,
            ROOT,
            args.skip_export,
            args.auto_review,
        )
        for line in logs:
            print(line)
            if line.startswith("  ✗"):
                failed += 1

    print(f"\n批处理完成，失败步骤: {failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
