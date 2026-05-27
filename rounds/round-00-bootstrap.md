# Round 00 — 仓库初始化（Bootstrap）

## 本轮目标

建立单仓库骨架、治理协议、设计文档、检查脚本，使后续 Agent 可按 Round 01–11 持续推进。

## 前置条件

无（从零创建）。

## 主要任务

- [x] 阅读并吸收 `novel-continuation-agent/governance/repo_protocol_standard.yaml`
- [x] 创建目录结构（apps、packages、docs、rounds、prompts、scripts、data、tests）
- [x] 撰写 11 份设计文档 + 4 份治理文档
- [x] 编写 `check_repo.py`、`init_data_dirs.py`
- [x] 初始化 Git 并推送公开 GitHub 仓库

## 输出文件

- 见 `docs/governance/update_log.md` 完整清单
- 核心：`scripts/check_repo.py`、`docs/DATA_MODEL.md`、`docs/governance/repo_protocol_standard.yaml`

## 验收标准

```bash
python scripts/check_repo.py
python scripts/init_data_dirs.py
python scripts/check_repo.py
```

两次 check 均输出「仓库骨架检查通过」。

## 本轮不做什么

- 不实现 ASR、LLM、对齐、UI、FFmpeg
- 不处理真实音频/文本
- 不写 API Key
- 不接真实 API

## 下一轮衔接（Round 01）

入口：`rounds/round-01-import-manifest.md`

实现 `project_manifest.json` / `chapter_manifest.json` schema 与导入占位。

## 状态

**已完成** — Round 00
