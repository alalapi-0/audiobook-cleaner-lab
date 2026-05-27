#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""反馈闭环单元测试。"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from packages.feedback_core.analyzer import analyze_feedback  # noqa: E402


class TestFeedbackAnalyzer(unittest.TestCase):
    """反馈分析测试。"""

    def test_diff_generates_lesson(self) -> None:
        """不一致决策生成 lesson。"""
        llm = {
            "decisions": [
                {"segment_id": "seg_0001", "action": "keep", "confidence": 0.9},
                {"segment_id": "seg_0002", "action": "delete", "confidence": 0.87},
            ]
        }
        review = {
            "review_session_id": "rev_test",
            "decisions": [
                {"segment_id": "seg_0001", "user_action": "keep"},
                {"segment_id": "seg_0002", "user_action": "keep"},
            ],
        }
        record = analyze_feedback("chapter_001", llm, review)
        self.assertEqual(record["stats"]["false_delete_risk"], 1)
        self.assertTrue(any("误删" in item["lesson"] for item in record["items"]))
        self.assertIn("lesson", record["items"][1])

    def test_agreement_stats(self) -> None:
        """一致率统计。"""
        llm = {
            "decisions": [
                {"segment_id": "seg_0001", "action": "keep", "confidence": 0.9},
            ]
        }
        review = {
            "decisions": [{"segment_id": "seg_0001", "user_action": "keep"}],
        }
        record = analyze_feedback("c1", llm, review)
        self.assertEqual(record["stats"]["agreement_count"], 1)


if __name__ == "__main__":
    unittest.main()
