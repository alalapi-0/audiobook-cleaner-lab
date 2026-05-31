# -*- coding: utf-8 -*-
"""LLM 真实 API 配置 — 从环境变量或 .env 读取，不输出密钥。"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _load_dotenv_file(path: Path) -> None:
    """将 KEY=VALUE 行写入 os.environ（不覆盖已存在的变量）。"""
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def load_llm_env(root: Path | None = None) -> None:
    """加载 .env 与 .env.local（若存在）。"""
    base = root or ROOT
    for name in (".env", ".env.local"):
        _load_dotenv_file(base / name)


@dataclass
class LlmApiConfig:
    """OpenAI 兼容 LLM API 配置。"""

    api_key: str
    base_url: str
    model: str
    timeout_sec: float = 120.0

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key.strip())

    @classmethod
    def from_env(cls, root: Path | None = None) -> LlmApiConfig:
        load_llm_env(root)
        api_key = (
            os.environ.get("LLM_API_KEY")
            or os.environ.get("OPENAI_API_KEY")
            or os.environ.get("OPENROUTER_API_KEY")
            or ""
        )
        base_url = (
            os.environ.get("LLM_BASE_URL")
            or os.environ.get("OPENAI_BASE_URL")
            or "https://api.openai.com/v1"
        ).rstrip("/")
        model = os.environ.get("LLM_MODEL") or os.environ.get("OPENAI_MODEL") or "gpt-4o-mini"
        timeout = float(os.environ.get("LLM_TIMEOUT_SEC", "120"))
        return cls(api_key=api_key, base_url=base_url, model=model, timeout_sec=timeout)
