# -*- coding: utf-8 -*-
"""原文与 ASR 文本规范化器。"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from packages.text_core.config import NormalizationConfig
from packages.text_core.filler_detector import detect_filler_candidates

# 半角 → 全角标点映射
_HALF_TO_FULL_PUNCT = str.maketrans({
    ",": "，",
    ".": "。",
    "!": "！",
    "?": "？",
    ";": "；",
    ":": "：",
})


def _normalize_whitespace(text: str) -> str:
    """清理行首行尾空白，合并连续空格，保留段落换行。"""
    lines = [re.sub(r"[ \t]+", " ", line.strip()) for line in text.splitlines()]
    # 合并多余空行
    result: list[str] = []
    prev_blank = False
    for line in lines:
        is_blank = line == ""
        if is_blank and prev_blank:
            continue
        result.append(line)
        prev_blank = is_blank
    return "\n".join(result).strip()


def _unify_punctuation(text: str) -> str:
    """统一中文标点为全角，省略号标准化。"""
    text = text.translate(_HALF_TO_FULL_PUNCT)
    text = re.sub(r"\.{3,}|…+", "……", text)
    return text


def _is_heading(line: str, config: NormalizationConfig) -> bool:
    """判断是否为章节标题行。"""
    for pattern in config.heading_patterns:
        if re.match(pattern, line.strip()):
            return True
    return False


def normalize_source_text(
    raw_text: str,
    chapter_id: str,
    source_path: str,
    config: NormalizationConfig | None = None,
) -> dict[str, Any]:
    """清洗用户提供的正确原文。"""
    cfg = config or NormalizationConfig.default()
    rules_applied: list[str] = ["whitespace_cleanup", "punctuation_unify"]

    text = _normalize_whitespace(raw_text)
    text = _unify_punctuation(text)
    rules_applied.append("fullwidth_halfwidth")

    # 标记标题行（不改变文本，仅记录规则）
    headings = [ln for ln in text.splitlines() if _is_heading(ln, cfg)]
    if headings:
        rules_applied.append("heading_detect")

    return {
        "chapter_id": chapter_id,
        "source": source_path,
        "normalized_text": text,
        "char_count": len(text),
        "rules_applied": rules_applied,
        "created_at": datetime.now().replace(microsecond=0).isoformat(),
    }


def normalize_asr_segments(
    transcript: dict[str, Any],
    config: NormalizationConfig | None = None,
) -> dict[str, Any]:
    """清洗 ASR segment 文本，保留 segment_id 映射与 filler 候选。"""
    cfg = config or NormalizationConfig.default()
    rules_applied = ["punctuation_strip", "whitespace_cleanup", "filler_detect"]

    output_segments: list[dict[str, Any]] = []
    for seg in transcript.get("segments", []):
        raw = seg.get("text", "")
        # ASR 口语标点噪声：去除 segment 内多余空格与半角标点
        normalized = re.sub(r"[ \t]+", "", raw.strip())
        normalized = normalized.translate(_HALF_TO_FULL_PUNCT)
        normalized = re.sub(r"[，,。！？；：、]+", "", normalized)

        fillers = detect_filler_candidates(normalized, cfg)
        output_segments.append(
            {
                "segment_id": seg["segment_id"],
                "normalized_text": normalized,
                "filler_candidates": fillers,
            }
        )

    return {
        "chapter_id": transcript.get("chapter_id", ""),
        "segments": output_segments,
        "rules_applied": rules_applied,
        "created_at": datetime.now().replace(microsecond=0).isoformat(),
    }
