# Round 01 — 素材导入与 Manifest

**状态：已完成（2026-05-27）**

## Round 目标

支持创建书籍项目、章节，登记音频与原文路径，生成 `project_manifest.json` 与 `chapter_manifest.json`。

## 前置条件

Round 00 验收通过。

## 主要任务

- 定义 manifest JSON schema（对齐 `DATA_MODEL.md`）
- 实现 CLI 或 API 占位：创建 project / 添加 chapter
- 校验路径存在性（不读大文件进 Git）
- 可选：SQLite 表设计草案

## 输出文件

- `packages/` 或 `apps/api/services/manifest_service.py`（占位）
- `tests/test_manifest_schema.py`（可选）
- 示例 manifest 写入 `data/`（本地，不提交）

## 验收标准

- 可生成合法 `project_manifest.json`、`chapter_manifest.json`
- schema 校验脚本或单元测试通过
- `python scripts/check_repo.py` 仍通过

## 不做什么

- 不跑 ASR
- 不把真实音频提交 Git

## 完成记录

- [x] `apps/api/schemas/manifest.py` — ProjectManifest / ChapterManifest schema
- [x] `apps/api/services/manifest_service.py` — 创建项目、添加章节、路径校验
- [x] `scripts/import_manifest.py` — CLI（create-project / add-chapter）
- [x] `tests/test_manifest_schema.py` — 6 项单元测试
- [x] `scripts/init_data_dirs.py` — 新增 `data/projects/`

## 验收结果

```bash
python3 scripts/check_repo.py          # 通过
python3 -m unittest tests.test_manifest_schema -v  # 6 tests OK
```

## 下一轮衔接

Round 02：`rounds/round-02-asr-baseline.md` — mock ASR 与 transcript.json
