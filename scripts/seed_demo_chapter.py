#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为本地 Review 演示生成 book_001/chapter_001 mock 流水线数据（仅写入 data/，不进 Git）。"""

from __future__ import annotations

import math
import struct
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

DEMO_AUDIO = ROOT / "data/raw_audio/book_001/chapter_001.wav"
DEMO_TEXT = ROOT / "data/source_text/book_001/chapter_001.txt"
MIN_DEMO_DURATION_SEC = 2.0


def _make_wav(path: Path, duration_sec: float = 5.0) -> None:
    """生成带简单音调的演示 wav，便于波形区可视化（非静音）。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    sample_rate = 16000
    n_samples = int(sample_rate * duration_sec)
    frames: list[bytes] = []
    for i in range(n_samples):
        t = i / sample_rate
        seg = int(t / max(duration_sec / 4, 0.25))
        amp = 0.12 + 0.08 * (seg % 3)
        freq = 180 + seg * 40
        val = int(amp * 32767 * math.sin(2 * math.pi * freq * t))
        val = max(-32767, min(32767, val))
        frames.append(struct.pack("<h", val))
    with wave.open(str(path), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(b"".join(frames))


def _wav_duration_sec(path: Path) -> float:
    if not path.is_file():
        return 0.0
    with wave.open(str(path), "r") as wf:
        return wf.getnframes() / float(wf.getframerate())


def _wav_needs_refresh(path: Path) -> bool:
    """过短或缺失的演示 wav 需要重新生成。"""
    return _wav_duration_sec(path) < MIN_DEMO_DURATION_SEC


def _run_pipeline(project_id: str, chapter_id: str) -> None:
    asr = AsrService(root=ROOT)
    norm = TextNormalizationService(root=ROOT)
    align = AlignmentService(root=ROOT)
    llm = LlmCutService(root=ROOT)
    asr.run_asr(project_id, chapter_id, MockAsrAdapter())
    norm.normalize_chapter(project_id, chapter_id)
    align.align_chapter(project_id, chapter_id)
    llm.run_llm_cut(project_id, chapter_id)


def seed_demo_chapter(
    project_id: str = "book_001",
    chapter_id: str = "chapter_001",
    *,
    force: bool = False,
    refresh_audio: bool = False,
) -> None:
    """创建演示章节并跑完 mock ASR → LLM 流水线。"""
    manifest = ManifestService(root=ROOT)
    chapter_path = manifest.chapter_manifest_path(project_id, chapter_id)
    audio = DEMO_AUDIO
    text = DEMO_TEXT

    if chapter_path.is_file() and not force:
        if refresh_audio and _wav_needs_refresh(audio):
            print(f"演示音频过短（{_wav_duration_sec(audio):.2f}s），正在更新 wav 并重跑流水线…")
            _make_wav(audio)
            _run_pipeline(project_id, chapter_id)
            print(f"✓ 已更新演示音频与 mock 数据: {project_id}/{chapter_id}")
            return
        print(f"✓ 章节已存在，跳过: {project_id}/{chapter_id}")
        return

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

    _run_pipeline(project_id, chapter_id)
    print(f"✓ 已生成 mock 演示数据: {project_id}/{chapter_id}")


def main() -> int:
    force = "--force" in sys.argv
    refresh_audio = "--refresh-audio" in sys.argv or force
    seed_demo_chapter(force=force, refresh_audio=refresh_audio)
    return 0


if __name__ == "__main__":
    sys.exit(main())
