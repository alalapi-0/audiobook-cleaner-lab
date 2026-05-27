#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""对齐模块单元测试。"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from packages.alignment_core.aligner import BaselineAligner  # noqa: E402
from packages.alignment_core.schemas.alignment import VALID_STATUSES, Alignment  # noqa: E402


class TestBaselineAligner(unittest.TestCase):
    """BaselineAligner 测试。"""

    def test_matched_and_extra_candidate(self) -> None:
        """匹配段与 extra_candidate 分类。"""
        source = "这是正确原文文本。后续段落内容。"
        segments = [
            {"segment_id": "seg_0001", "normalized_text": "这是正确原文文本"},
            {"segment_id": "seg_0002", "normalized_text": "嗯不对我重新读"},
        ]
        aligner = BaselineAligner()
        alignment = aligner.align("chapter_001", source, segments)

        self.assertEqual(alignment.validate(), [])
        statuses = {item.status for item in alignment.items}
        self.assertIn("matched", statuses)
        self.assertIn("extra_candidate", statuses)

    def test_all_statuses_valid(self) -> None:
        """所有 status 均在合法枚举内。"""
        source = "第一章测试内容重复重复。"
        segments = [
            {"segment_id": "seg_0001", "normalized_text": "第一章测试"},
            {"segment_id": "seg_0002", "normalized_text": "第一章测试"},
            {"segment_id": "seg_0003", "normalized_text": "完全无关的废话"},
        ]
        alignment = BaselineAligner().align("c1", source, segments)
        for item in alignment.items:
            self.assertIn(item.status, VALID_STATUSES)

    def test_alignment_roundtrip(self) -> None:
        """Alignment 序列化往返。"""
        source = "短文本。"
        segments = [{"segment_id": "seg_0001", "normalized_text": "短文本"}]
        alignment = BaselineAligner().align("c1", source, segments)
        restored = Alignment.from_dict(alignment.to_dict())
        self.assertEqual(len(restored.items), len(alignment.items))


if __name__ == "__main__":
    unittest.main()
