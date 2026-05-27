# llm_core — LLM 机切建议（mock / 真实 Adapter）

from packages.llm_core.adapters.mock import MockLlmAdapter
from packages.llm_core.service import LlmCutService

__all__ = ["MockLlmAdapter", "LlmCutService"]
