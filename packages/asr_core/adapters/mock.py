# -*- coding: utf-8 -*-
"""Mock ASR Adapter — 不读取真实音频内容，仅估算时长并生成示例 segment。"""

from __future__ import annotations

import wave
from pathlib import Path
from typing import Any

from packages.asr_core.base import AsrAdapter
from packages.asr_core.schemas.transcript import Transcript, TranscriptSegment

# mock 示例文本（中文有声书场景）
_MOCK_TEXTS = [
    "这是识别出来的文本",
    "嗯，不对，我重新读",
    "话说那日天色已晚",
    "他缓缓走进房间",
]


class MockAsrAdapter(AsrAdapter):
    """返回固定模式的 mock transcript，用于开发与测试。"""

    DEFAULT_DURATION_SEC = 3600.0

    @property
    def engine_name(self) -> str:
        return "mock"

    def _estimate_duration(self, audio_path: Path) -> float:
        """估算音频时长（秒）。WAV 读 header，其他格式用默认值。"""
        if audio_path.suffix.lower() == ".wav":
            try:
                with wave.open(str(audio_path), "rb") as wf:
                    frames = wf.getnframes()
                    rate = wf.getframerate()
                    if rate > 0:
                        return max(frames / rate, 1.0)
            except (wave.Error, OSError):
                pass
        return self.DEFAULT_DURATION_SEC

    def transcribe(
        self,
        audio_path: str,
        chapter_id: str,
        project_id: str,
    ) -> dict[str, Any]:
        """生成 mock transcript，不解析音频 PCM 内容。"""
        path = Path(audio_path)
        duration = self._estimate_duration(path)

        # 将时长均分为 4 段
        seg_count = len(_MOCK_TEXTS)
        seg_len = duration / seg_count
        segments: list[TranscriptSegment] = []
        for i, text in enumerate(_MOCK_TEXTS):
            start = round(i * seg_len, 2)
            end = round((i + 1) * seg_len, 2) if i < seg_count - 1 else round(duration, 2)
            segments.append(
                TranscriptSegment(
                    segment_id=f"seg_{i + 1:04d}",
                    start=start,
                    end=end,
                    text=text,
                    confidence=0.95 - i * 0.02,
                )
            )

        transcript = Transcript(
            chapter_id=chapter_id,
            project_id=project_id,
            asr_engine=self.engine_name,
            duration_sec=round(duration, 2),
            segments=segments,
        )
        errors = transcript.validate()
        if errors:
            raise ValueError(f"mock transcript 校验失败: {'; '.join(errors)}")
        return transcript.to_dict()
