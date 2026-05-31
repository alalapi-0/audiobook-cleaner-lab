# -*- coding: utf-8 -*-
"""LLM Adapter 实现。"""

from packages.llm_core.adapters.mock import MockLlmAdapter

__all__ = ["MockLlmAdapter", "OpenAiCompatibleAdapter"]


def __getattr__(name: str):
    if name == "OpenAiCompatibleAdapter":
        from packages.llm_core.adapters.openai_compatible import OpenAiCompatibleAdapter

        return OpenAiCompatibleAdapter
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
