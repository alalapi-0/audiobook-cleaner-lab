# 数据模型（DATA_MODEL）

本文档定义流水线中 11 种核心 JSON 结构。所有路径默认相对于仓库根目录，实际文件存于 `data/` 下且不提交 Git。

---

## 1. project_manifest.json

书籍级项目元数据。

```json
{
  "project_id": "book_001",
  "book_title": "示例有声书",
  "language": "zh-CN",
  "created_at": "2026-01-01T00:00:00",
  "updated_at": "2026-01-01T00:00:00",
  "chapters": [
    {
      "chapter_id": "chapter_001",
      "title": "第一章",
      "status": "imported",
      "order": 1
    },
    {
      "chapter_id": "chapter_002",
      "title": "第二章",
      "status": "pending",
      "order": 2
    }
  ],
  "defaults": {
    "asr_engine": "mock",
    "llm_engine": "mock",
    "export_format": "mp3"
  }
}
```

| 字段 | 说明 |
|------|------|
| `project_id` | 唯一书籍 ID |
| `chapters[].status` | imported / asr_done / aligned / reviewed / exported |
| `defaults` | 默认 Adapter 与导出格式 |

---

## 2. chapter_manifest.json

章节级素材路径与处理状态。

```json
{
  "chapter_id": "chapter_001",
  "project_id": "book_001",
  "title": "第一章",
  "source_audio": "data/raw_audio/book_001/chapter_001.wav",
  "source_text": "data/source_text/book_001/chapter_001.txt",
  "status": "imported",
  "artifacts": {
    "transcript": "data/transcripts/book_001/chapter_001.json",
    "normalized_source": "data/normalized/book_001/chapter_001_source.json",
    "normalized_asr": "data/normalized/book_001/chapter_001_asr.json",
    "alignment": "data/alignments/book_001/chapter_001.json",
    "llm_decision": "data/cut_plans/book_001/chapter_001_llm.json",
    "cut_plan": "data/cut_plans/book_001/chapter_001.json",
    "user_review": "data/reviews/book_001/chapter_001.json",
    "export": "data/exports/book_001/chapter_001_clean.mp3"
  },
  "created_at": "2026-01-01T00:00:00"
}
```

---

## 3. transcript.json

ASR 转写结果，segment 级时间戳。

```json
{
  "chapter_id": "chapter_001",
  "project_id": "book_001",
  "asr_engine": "mock",
  "duration_sec": 3600.5,
  "segments": [
    {
      "segment_id": "seg_0001",
      "start": 0.0,
      "end": 4.82,
      "text": "这是识别出来的文本",
      "confidence": 0.95
    },
    {
      "segment_id": "seg_0002",
      "start": 4.82,
      "end": 8.15,
      "text": "嗯，不对，我重新读",
      "confidence": 0.88
    }
  ],
  "created_at": "2026-01-02T10:00:00"
}
```

---

## 4. normalized_source_text.json

清洗后的正确原文。

```json
{
  "chapter_id": "chapter_001",
  "source": "data/source_text/book_001/chapter_001.txt",
  "normalized_text": "这是正确原文文本。后续段落……",
  "char_count": 15230,
  "rules_applied": [
    "punctuation_unify",
    "whitespace_cleanup",
    "fullwidth_halfwidth"
  ],
  "created_at": "2026-01-02T11:00:00"
}
```

---

## 5. normalized_asr_text.json

清洗后的 ASR 文本（保留 segment 映射）。

```json
{
  "chapter_id": "chapter_001",
  "segments": [
    {
      "segment_id": "seg_0001",
      "normalized_text": "这是识别出来的文本",
      "filler_candidates": []
    },
    {
      "segment_id": "seg_0002",
      "normalized_text": "嗯不对我重新读",
      "filler_candidates": [
        { "token": "嗯", "type": "filler", "auto_delete": false }
      ]
    }
  ],
  "rules_applied": ["punctuation_strip", "filler_detect"],
  "created_at": "2026-01-02T11:05:00"
}
```

---

## 6. alignment.json

原文与 ASR 对齐结果。

```json
{
  "chapter_id": "chapter_001",
  "alignment_engine": "baseline_v1",
  "items": [
    {
      "alignment_id": "align_0001",
      "asr_segment_id": "seg_0001",
      "source_range": { "start_char": 0, "end_char": 8 },
      "asr_text": "这是识别出来的文本",
      "source_text": "这是正确原文文本",
      "similarity": 0.92,
      "status": "matched"
    },
    {
      "alignment_id": "align_0002",
      "asr_segment_id": "seg_0002",
      "source_range": null,
      "asr_text": "嗯不对我重新读",
      "source_text": null,
      "similarity": 0.15,
      "status": "extra_candidate"
    }
  ],
  "created_at": "2026-01-02T12:00:00"
}
```

**status 枚举**：`matched` | `extra_candidate` | `missing` | `repeated` | `uncertain` | `low_similarity`

---

## 7. llm_cut_decision.json

大模型机切建议（**仅文本层，不直接切音频**）。

```json
{
  "chapter_id": "chapter_001",
  "llm_engine": "mock",
  "decisions": [
    {
      "segment_id": "seg_0001",
      "action": "keep",
      "reason_type": "matches_source",
      "reason": "与原文匹配，保留",
      "suggested_cut": null,
      "confidence": 0.96
    },
    {
      "segment_id": "seg_0002",
      "action": "delete",
      "reason_type": "restart_phrase",
      "reason": "该片段是重读前的废弃内容，不属于原文",
      "suggested_cut": {
        "start": 4.82,
        "end": 8.15,
        "pre_padding": 0.08,
        "post_padding": 0.12
      },
      "confidence": 0.87
    },
    {
      "segment_id": "seg_0003",
      "action": "uncertain",
      "reason_type": "ambiguous_filler",
      "reason": "可能是语气词或正文，需人工确认",
      "suggested_cut": {
        "start": 8.15,
        "end": 9.0,
        "pre_padding": 0.05,
        "post_padding": 0.05
      },
      "confidence": 0.52
    }
  ],
  "created_at": "2026-01-02T13:00:00"
}
```

**action**：`keep` | `delete` | `uncertain`

**reason_type 示例**：`matches_source` | `restart_phrase` | `off_script` | `filler` | `misread` | `ambiguous_filler` | `low_confidence`

---

## 8. cut_plan.json

用户确认后的最终切点计划（FFmpeg 输入）。

```json
{
  "chapter_id": "chapter_001",
  "source_audio": "data/raw_audio/book_001/chapter_001.wav",
  "version": 2,
  "delete_ranges": [
    {
      "range_id": "del_001",
      "start": 4.74,
      "end": 8.27,
      "reason": "restart_phrase",
      "source_segment_ids": ["seg_0002"],
      "confirmed_by_user": true
    }
  ],
  "keep_ranges": [
    {
      "range_id": "keep_001",
      "start": 0.0,
      "end": 4.74,
      "source_segment_ids": ["seg_0001"]
    }
  ],
  "export": {
    "format": "mp3",
    "bitrate": "192k",
    "output_path": "data/exports/book_001/chapter_001_clean.mp3"
  },
  "updated_at": "2026-01-03T09:00:00"
}
```

---

## 9. user_review.json

人工校正过程记录。

```json
{
  "chapter_id": "chapter_001",
  "review_session_id": "rev_20260103_001",
  "decisions": [
    {
      "segment_id": "seg_0002",
      "model_action": "delete",
      "user_action": "delete",
      "user_adjusted_cut": {
        "start": 4.74,
        "end": 8.27
      },
      "note": "同意删除，切点略放宽",
      "reviewed_at": "2026-01-03T09:00:00"
    },
    {
      "segment_id": "seg_0003",
      "model_action": "uncertain",
      "user_action": "keep",
      "user_adjusted_cut": null,
      "note": "确认是正文语气，保留",
      "reviewed_at": "2026-01-03T09:05:00"
    }
  ],
  "completed": true
}
```

---

## 10. feedback_record.json

模型建议 vs 用户最终决策的差异与学习点。

```json
{
  "chapter_id": "chapter_001",
  "segment_id": "seg_0002",
  "model_decision": {
    "action": "delete",
    "start": 4.82,
    "end": 8.15,
    "confidence": 0.87,
    "reason_type": "restart_phrase"
  },
  "user_final_decision": {
    "action": "delete",
    "start": 4.74,
    "end": 8.27
  },
  "delta": {
    "start_shift": -0.08,
    "end_shift": 0.12,
    "action_changed": false
  },
  "lesson": "模型切点偏紧，后续应增加 post_padding 默认值",
  "recorded_at": "2026-01-03T09:30:00"
}
```

---

## 11. export_report.json

FFmpeg 导出结果报告。

```json
{
  "chapter_id": "chapter_001",
  "source_audio": "data/raw_audio/book_001/chapter_001.wav",
  "output_path": "data/exports/book_001/chapter_001_clean.mp3",
  "export_mode": "ffmpeg",
  "dry_run": false,
  "source_duration_sec": 3600.5,
  "output_duration_sec": 3542.1,
  "deleted_duration_sec": 58.4,
  "delete_range_count": 12,
  "ffmpeg_command": "ffmpeg -i ... -filter_complex ...",
  "status": "success",
  "exported_at": "2026-01-03T10:00:00"
}
```

---

## 文件存放约定

| JSON 类型 | 默认目录 |
|-----------|----------|
| manifest | `data/` 根或按 book 子目录 |
| transcript | `data/transcripts/` |
| normalized | `data/normalized/` |
| alignment | `data/alignments/` |
| llm / cut_plan | `data/cut_plans/` |
| review | `data/reviews/` |
| export | `data/exports/` + 报告同目录 |

## 版本化

- 每种 JSON 应含 `created_at` / `updated_at`
- schema 变更时在 `docs/governance/update_log.md` 记录
