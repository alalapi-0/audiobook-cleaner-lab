# -*- coding: utf-8 -*-
"""LLM Adapter 抽象基类。"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class LlmAdapter(ABC):
    """LLM 机切建议可替换 Adapter 接口。"""

    @property
    @abstractmethod
    def engine_name(self) -> str:
        """引擎标识。"""

    @abstractmethod
    def decide(self, payload: dict[str, Any]) -> dict[str, Any]:
        """基于 alignment + transcript 上下文输出 llm_cut_decision。"""
