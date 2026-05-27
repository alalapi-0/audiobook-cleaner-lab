# -*- coding: utf-8 -*-
"""语气词/废话候选检测 — 仅标记，不自动删除。"""

from __future__ import annotations

import re
from typing import Any

from packages.text_core.config import NormalizationConfig


def detect_filler_candidates(
    text: str,
    config: NormalizationConfig | None = None,
) -> list[dict[str, Any]]:
    """检测 segment 中的 filler 候选。

    规则：句首孤立出现的配置 token 标记为 filler，auto_delete 恒为 false。
    """
    cfg = config or NormalizationConfig.default()
    candidates: list[dict[str, Any]] = []
    stripped = text.strip()

    for token in cfg.filler_tokens:
        # 句首 token，后接标点或继续文本
        pattern = rf"^{re.escape(token)}([，,。！？；：、\s]|)"
        if re.match(pattern, stripped):
            candidates.append(
                {
                    "token": token,
                    "type": "filler",
                    "auto_delete": False,
                    "note": "候选，需结合 alignment 与 LLM 判断",
                }
            )
    return candidates
