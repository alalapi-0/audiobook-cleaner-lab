# -*- coding: utf-8 -*-
"""ASR Adapter 抽象基类。"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AsrAdapter(ABC):
    """ASR 可替换 Adapter 接口。"""

    @property
    @abstractmethod
    def engine_name(self) -> str:
        """引擎标识，写入 transcript.asr_engine。"""

    @abstractmethod
    def transcribe(
        self,
        audio_path: str,
        chapter_id: str,
        project_id: str,
    ) -> dict[str, Any]:
        """转写音频，返回符合 DATA_MODEL 的 transcript 字典。"""
