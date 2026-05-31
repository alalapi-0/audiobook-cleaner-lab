# llm_core — LLM 机切建议（mock / 真实 Adapter）

from packages.llm_core.adapters.mock import MockLlmAdapter
from packages.llm_core.config import LlmApiConfig
from packages.llm_core.service import LlmCutService

__all__ = ["MockLlmAdapter", "OpenAiCompatibleAdapter", "LlmApiConfig", "LlmCutService"]


def __getattr__(name: str):
    if name == "OpenAiCompatibleAdapter":
        from packages.llm_core.adapters.openai_compatible import OpenAiCompatibleAdapter

        return OpenAiCompatibleAdapter
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
