# -*- coding: utf-8 -*-
"""文本规范化配置。"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class NormalizationConfig:
    """文本清洗规则配置。"""

    punctuation_mode: str = "fullwidth"
    filler_tokens: list[str] = field(
        default_factory=lambda: ["嗯", "啊", "呃", "那个", "就是", "然后"]
    )
    heading_patterns: list[str] = field(
        default_factory=lambda: [r"^第[一二三四五六七八九十百千\d]+章"]
    )

    @classmethod
    def default(cls) -> NormalizationConfig:
        """默认配置。"""
        return cls()
