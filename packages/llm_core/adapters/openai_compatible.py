# -*- coding: utf-8 -*-
"""OpenAI 兼容 LLM Adapter — 调用 Chat Completions API 输出机切建议。"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import httpx

from packages.llm_core.base import LlmAdapter
from packages.llm_core.config import LlmApiConfig
from packages.llm_core.schemas.llm_cut_decision import LlmCutDecision

ROOT = Path(__file__).resolve().parents[3]
SYSTEM_PROMPT_PATH = ROOT / "prompts" / "llm_cut_decision" / "system_openai.md"


def _extract_json(text: str) -> dict[str, Any]:
    """从模型回复中提取 JSON 对象。"""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("模型回复中未找到 JSON 对象")
    return json.loads(text[start : end + 1])


class OpenAiCompatibleAdapter(LlmAdapter):
    """OpenAI / OpenRouter / 本地兼容端点 Adapter。"""

    def __init__(self, config: LlmApiConfig | None = None) -> None:
        self.config = config or LlmApiConfig.from_env()
        if not self.config.is_configured:
            raise RuntimeError(
                "LLM API 未配置：请设置 LLM_API_KEY 或 OPENAI_API_KEY（.env 或环境变量）"
            )
        self._system_prompt = self._load_system_prompt()

    @property
    def engine_name(self) -> str:
        return "openai_compatible"

    def _load_system_prompt(self) -> str:
        if SYSTEM_PROMPT_PATH.is_file():
            return SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
        return "你是中文有声书机切助手，仅输出 llm_cut_decision JSON。"

    def _call_api(self, payload: dict[str, Any]) -> str:
        url = f"{self.config.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": self.config.model,
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": self._system_prompt},
                {
                    "role": "user",
                    "content": json.dumps(payload, ensure_ascii=False),
                },
            ],
        }
        with httpx.Client(timeout=self.config.timeout_sec) as client:
            resp = client.post(url, headers=headers, json=body)
            resp.raise_for_status()
            data = resp.json()
        choices = data.get("choices") or []
        if not choices:
            raise RuntimeError("API 返回空 choices")
        return str(choices[0].get("message", {}).get("content", ""))

    def decide(self, payload: dict[str, Any]) -> dict[str, Any]:
        """调用真实 LLM API 输出 llm_cut_decision。"""
        raw = self._call_api(payload)
        parsed = _extract_json(raw)
        parsed["chapter_id"] = payload.get("chapter_id", parsed.get("chapter_id", ""))
        parsed["llm_engine"] = self.engine_name

        decision = LlmCutDecision.from_dict(parsed)
        errors = decision.validate()
        if errors:
            raise ValueError(f"LLM 输出 schema 校验失败: {'; '.join(errors)}")
        return decision.to_dict()
