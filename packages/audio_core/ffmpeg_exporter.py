# -*- coding: utf-8 -*-
"""FFmpeg 非破坏式导出 — 根据 cut_plan 删除区间并导出干净音频。"""

from __future__ import annotations

import json
import shutil
import subprocess
import wave
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class ExportResult:
    """导出结果。"""

    success: bool
    command: str
    output_path: str
    input_duration_sec: float
    output_duration_sec: float | None
    deleted_sec: float
    dry_run: bool
    error: str | None = None

    def to_report(self, chapter_id: str) -> dict[str, Any]:
        """生成 export_report.json 结构。"""
        return {
            "chapter_id": chapter_id,
            "success": self.success,
            "dry_run": self.dry_run,
            "ffmpeg_command": self.command,
            "input_duration_sec": round(self.input_duration_sec, 3),
            "output_duration_sec": round(self.output_duration_sec or 0, 3)
            if self.output_duration_sec
            else None,
            "deleted_sec": round(self.deleted_sec, 3),
            "output_path": self.output_path,
            "error": self.error,
            "created_at": datetime.now().replace(microsecond=0).isoformat(),
        }


def _get_wav_duration(path: Path) -> float:
    """读取 WAV 时长（秒）。"""
    with wave.open(str(path), "rb") as wf:
        rate = wf.getframerate()
        if rate <= 0:
            return 0.0
        return wf.getnframes() / rate


def _build_aselect_filter(delete_ranges: list[dict[str, Any]]) -> str:
    """构建 aselect 滤镜表达式，排除 delete 区间。"""
    if not delete_ranges:
        return "anull"

    conditions: list[str] = []
    for dr in delete_ranges:
        start = float(dr["start"])
        end = float(dr["end"])
        conditions.append(f"between(t,{start},{end})")

    # not(cond1+cond2+...) — 保留不在任何 delete 区间的样本
    joined = "+".join(conditions)
    return f"aselect='not({joined})',asetpts=N/SR/TB"


class FfmpegExporter:
    """FFmpeg 导出器 — 不覆盖原始音频。"""

    def __init__(self, ffmpeg_bin: str | None = None) -> None:
        self.ffmpeg_bin = ffmpeg_bin or shutil.which("ffmpeg") or "ffmpeg"

    def _probe_duration(self, input_path: Path) -> float:
        """探测输入音频时长。"""
        if input_path.suffix.lower() == ".wav":
            try:
                return _get_wav_duration(input_path)
            except (wave.Error, OSError):
                pass
        return 0.0

    def build_command(
        self,
        input_path: Path,
        output_path: Path,
        cut_plan: dict[str, Any],
    ) -> str:
        """构建 ffmpeg 命令字符串。"""
        delete_ranges = cut_plan.get("delete_ranges", [])
        export_cfg = cut_plan.get("export", {})
        fmt = export_cfg.get("format", "mp3")
        bitrate = export_cfg.get("bitrate", "192k")

        af_filter = _build_aselect_filter(delete_ranges)

        if fmt == "mp3":
            codec_args = f"-c:a libmp3lame -b:a {bitrate}"
        elif fmt == "wav":
            codec_args = "-c:a pcm_s16le"
        else:
            codec_args = f"-c:a libmp3lame -b:a {bitrate}"

        cmd = (
            f"{self.ffmpeg_bin} -y -i {input_path!s} "
            f"-af \"{af_filter}\" {codec_args} {output_path!s}"
        )
        return cmd

    def export(
        self,
        cut_plan: dict[str, Any],
        root: Path,
        dry_run: bool = False,
    ) -> ExportResult:
        """执行或 dry-run 导出。"""
        source_rel = cut_plan.get("source_audio", "")
        input_path = Path(source_rel)
        if not input_path.is_absolute():
            input_path = root / source_rel

        export_cfg = cut_plan.get("export", {})
        output_rel = export_cfg.get("output_path", "")
        output_path = Path(output_rel)
        if not output_path.is_absolute():
            output_path = root / output_rel

        if not input_path.is_file():
            return ExportResult(
                success=False,
                command="",
                output_path=str(output_path),
                input_duration_sec=0.0,
                output_duration_sec=None,
                deleted_sec=0.0,
                dry_run=dry_run,
                error=f"源音频不存在: {input_path}",
            )

        delete_ranges = cut_plan.get("delete_ranges", [])
        deleted_sec = sum(
            float(dr["end"]) - float(dr["start"]) for dr in delete_ranges
        )
        input_dur = self._probe_duration(input_path)
        command = self.build_command(input_path, output_path, cut_plan)

        if dry_run:
            return ExportResult(
                success=True,
                command=command,
                output_path=str(output_path.relative_to(root)),
                input_duration_sec=input_dur,
                output_duration_sec=max(0.0, input_dur - deleted_sec),
                deleted_sec=deleted_sec,
                dry_run=True,
            )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        # 解析命令为 argv（简化：固定格式）
        af_filter = _build_aselect_filter(delete_ranges)
        fmt = export_cfg.get("format", "mp3")
        bitrate = export_cfg.get("bitrate", "192k")

        cmd_args = [
            self.ffmpeg_bin,
            "-y",
            "-i",
            str(input_path),
            "-af",
            af_filter,
        ]
        if fmt == "mp3":
            cmd_args.extend(["-c:a", "libmp3lame", "-b:a", bitrate])
        else:
            cmd_args.extend(["-c:a", "pcm_s16le"])
        cmd_args.append(str(output_path))

        try:
            subprocess.run(
                cmd_args,
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as exc:
            return ExportResult(
                success=False,
                command=command,
                output_path=str(output_path.relative_to(root)),
                input_duration_sec=input_dur,
                output_duration_sec=None,
                deleted_sec=deleted_sec,
                dry_run=False,
                error=exc.stderr or str(exc),
            )

        out_dur = self._probe_duration(output_path) if output_path.suffix == ".wav" else None
        if out_dur is None and output_path.is_file():
            out_dur = max(0.0, input_dur - deleted_sec)

        return ExportResult(
            success=True,
            command=command,
            output_path=str(output_path.relative_to(root)),
            input_duration_sec=input_dur,
            output_duration_sec=out_dur,
            deleted_sec=deleted_sec,
            dry_run=False,
        )

    def write_export_report(
        self,
        result: ExportResult,
        chapter_id: str,
        report_path: Path,
    ) -> None:
        """写入 export_report.json。"""
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(result.to_report(chapter_id), ensure_ascii=False, indent=2)
            + "\n",
            encoding="utf-8",
        )
