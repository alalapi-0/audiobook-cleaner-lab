#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为本地 Review 演示生成 book_001/chapter_001 mock 流水线数据（仅写入 data/，不进 Git）。"""

from __future__ import annotations

import sys
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.api.services.manifest_service import ManifestError, ManifestService  # noqa: E402
from packages.alignment_core.service import AlignmentService  # noqa: E402
from packages.asr_core.adapters import MockAsrAdapter  # noqa: E402
from packages.asr_core.service import AsrService  # noqa: E402
from packages.llm_core.service import LlmCutService  # noqa: E402
from packages.text_core.service import TextNormalizationService  # noqa: E402


def _make_wav(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(b"\x00\x00" * 16000)


def seed_demo_chapter(
    project_id: str = "book_001",
    chapter_id: str = "chapter_001",
    *,
    force: bool = False,
) -> None:
    """创建演示章节并跑完 mock ASR → LLM 流水线。"""
    manifest = ManifestService(root=ROOT)
    chapter_path = manifest.chapter_manifest_path(project_id, chapter_id)
    if chapter_path.is_file() and not force:
        print(f"✓ 章节已存在，跳过: {project_id}/{chapter_id}")
        return

    audio = ROOT / "data/raw_audio/book_001/chapter_001.wav"
    text = ROOT / "data/source_text/book_001/chapter_001.txt"
    _make_wav(audio)
    text.parent.mkdir(parents=True, exist_ok=True)
    text.write_text("这是正确原文文本。后续段落内容。", encoding="utf-8")

    try:
        manifest.create_project(project_id, "示例有声书")
    except ManifestError:
        pass

    if not chapter_path.is_file():
        manifest.add_chapter(
            project_id=project_id,
            chapter_id=chapter_id,
            title="第一章",
            source_audio="data/raw_audio/book_001/chapter_001.wav",
            source_text="data/source_text/book_001/chapter_001.txt",
        )

    asr = AsrService(root=ROOT)
    norm = TextNormalizationService(root=ROOT)
    align = AlignmentService(root=ROOT)
    llm = LlmCutService(root=ROOT)

    asr.run_asr(project_id, chapter_id, MockAsrAdapter())
    norm.normalize_chapter(project_id, chapter_id)
    align.align_chapter(project_id, chapter_id)
    llm.run_llm_cut(project_id, chapter_id)

    print(f"✓ 已生成 mock 演示数据: {project_id}/{chapter_id}")


def main() -> int:
    force = "--force" in sys.argv
    seed_demo_chapter(force=force)
    return 0


if __name__ == "__main__":
    sys.exit(main())
