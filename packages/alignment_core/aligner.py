# -*- coding: utf-8 -*-
"""基础对齐器 — 滑动窗口 + SequenceMatcher 相似度。"""

from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher

from packages.alignment_core.schemas.alignment import Alignment, AlignmentItem, SourceRange

# 相似度阈值（可配置）
MATCHED_THRESHOLD = 0.85
UNCERTAIN_THRESHOLD = 0.50


@dataclass
class AlignerConfig:
    """对齐器配置。"""

    matched_threshold: float = MATCHED_THRESHOLD
    uncertain_threshold: float = UNCERTAIN_THRESHOLD
    window_slack: float = 0.3  # 窗口长度 = len(asr) * (1 + slack)


def _similarity(a: str, b: str) -> float:
    """计算两字符串相似度 ratio。"""
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def _find_best_window(source: str, asr_text: str, search_start: int) -> tuple[int, int, float]:
    """在原文中滑动搜索 ASR 文本最佳匹配窗口。"""
    if not asr_text:
        return search_start, search_start, 0.0

    asr_len = len(asr_text)
    min_win = max(1, int(asr_len * 0.7))
    max_win = max(asr_len, int(asr_len * (1 + AlignerConfig.window_slack)))
    best_score = 0.0
    best_start = search_start
    best_end = search_start

    # 从 search_start 起向后搜索
    for start in range(search_start, len(source)):
        for win_len in range(min_win, max_win + 1):
            end = start + win_len
            if end > len(source):
                break
            chunk = source[start:end]
            score = _similarity(asr_text, chunk)
            if score > best_score:
                best_score = score
                best_start = start
                best_end = end

    return best_start, best_end, best_score


def _classify_status(similarity: float, cfg: AlignerConfig) -> str:
    """根据相似度分类 status。"""
    if similarity >= cfg.matched_threshold:
        return "matched"
    if similarity >= cfg.uncertain_threshold:
        return "uncertain"
    return "low_similarity"


class BaselineAligner:
    """baseline_v1 对齐器 — 以 ASR segment 为单元贪心匹配原文。"""

    ENGINE_NAME = "baseline_v1"

    def __init__(self, config: AlignerConfig | None = None) -> None:
        self.config = config or AlignerConfig()

    def align(
        self,
        chapter_id: str,
        source_text: str,
        asr_segments: list[dict],
    ) -> Alignment:
        """执行对齐，返回 Alignment 对象。"""
        cfg = self.config
        items: list[AlignmentItem] = []
        search_cursor = 0
        used_ranges: list[tuple[int, int]] = []

        for idx, seg in enumerate(asr_segments):
            asr_text = seg.get("normalized_text", "")
            seg_id = seg.get("segment_id", f"seg_{idx + 1:04d}")

            start, end, score = _find_best_window(source_text, asr_text, search_cursor)

            if score < cfg.uncertain_threshold:
                # 无法在原文找到对应
                items.append(
                    AlignmentItem(
                        alignment_id=f"align_{len(items) + 1:04d}",
                        asr_segment_id=seg_id,
                        source_range=None,
                        asr_text=asr_text,
                        source_text=None,
                        similarity=round(score, 4),
                        status="extra_candidate",
                    )
                )
                continue

            status = _classify_status(score, cfg)
            source_snippet = source_text[start:end]

            # 检测 repeated：同一原文区间已被匹配
            for used_start, used_end in used_ranges:
                if start < used_end and end > used_start:
                    status = "repeated"
                    break

            items.append(
                AlignmentItem(
                    alignment_id=f"align_{len(items) + 1:04d}",
                    asr_segment_id=seg_id,
                    source_range=SourceRange(start_char=start, end_char=end),
                    asr_text=asr_text,
                    source_text=source_snippet,
                    similarity=round(score, 4),
                    status=status,
                )
            )
            used_ranges.append((start, end))
            if status == "matched":
                search_cursor = end

        # 检测 missing：原文尾部未被覆盖的区间（简化：search_cursor 之后的内容）
        if search_cursor < len(source_text.strip()):
            remaining = source_text[search_cursor:].strip()
            if remaining:
                items.append(
                    AlignmentItem(
                        alignment_id=f"align_{len(items) + 1:04d}",
                        asr_segment_id=None,
                        source_range=SourceRange(
                            start_char=search_cursor,
                            end_char=len(source_text),
                        ),
                        asr_text=None,
                        source_text=remaining,
                        similarity=0.0,
                        status="missing",
                    )
                )

        alignment = Alignment(
            chapter_id=chapter_id,
            alignment_engine=self.ENGINE_NAME,
            items=items,
        )
        errors = alignment.validate()
        if errors:
            raise ValueError(f"alignment 校验失败: {'; '.join(errors)}")
        return alignment
