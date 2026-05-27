# -*- coding: utf-8 -*-
"""ImportTranscriptAdapter — 读取用户提供的 transcript.json 并校验 schema。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from packages.asr_core.base import AsrAdapter
from packages.asr_core.schemas.transcript import Transcript


class ImportTranscriptAdapter(AsrAdapter):
    """导入外部 ASR 结果，校验后返回标准 transcript 结构。"""

    def __init__(self, import_path: str) -> None:
        self.import_path = import_path

    @property
    def engine_name(self) -> str:
        return "import"

    def transcribe(
        self,
        audio_path: str,
        chapter_id: str,
        project_id: str,
    ) -> dict[str, Any]:
        """读取并校验外部 transcript.json。"""
        path = Path(self.import_path)
        if not path.is_file():
            raise FileNotFoundError(f"transcript 文件不存在: {self.import_path}")

        data = json.loads(path.read_text(encoding="utf-8"))
        # 允许用户文件缺少 chapter/project，此处补全
        data.setdefault("chapter_id", chapter_id)
        data.setdefault("project_id", project_id)
        data.setdefault("asr_engine", "import")

        transcript = Transcript.from_dict(data)
        # 强制与当前章节一致
        transcript.chapter_id = chapter_id
        transcript.project_id = project_id

        errors = transcript.validate()
        if errors:
            raise ValueError(f"导入 transcript 校验失败: {'; '.join(errors)}")
        return transcript.to_dict()
