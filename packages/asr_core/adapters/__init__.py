# -*- coding: utf-8 -*-
"""ASR Adapter 实现。"""

from packages.asr_core.adapters.import_adapter import ImportTranscriptAdapter
from packages.asr_core.adapters.mock import MockAsrAdapter

__all__ = ["MockAsrAdapter", "ImportTranscriptAdapter"]
