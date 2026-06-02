#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""仓库骨架检查脚本 — Round 00 验收用，无第三方依赖。"""

from __future__ import annotations

import sys
from pathlib import Path

# 仓库根目录（scripts/ 的上一级）
ROOT = Path(__file__).resolve().parent.parent

# 必须存在的关键目录
REQUIRED_DIRS = [
    "apps/api/routes",
    "apps/api/services",
    "apps/web/src",
    "apps/web/public",
    "packages/audio_core",
    "packages/asr_core",
    "packages/text_core",
    "packages/alignment_core",
    "packages/llm_core",
    "packages/feedback_core",
    "data",
    "docs",
    "docs/governance",
    "rounds",
    "prompts/system",
    "prompts/round_prompts",
    "prompts/llm_cut_decision",
    "scripts",
    "tests",
]

# 必须存在的关键文件
REQUIRED_FILES = [
    "README.md",
    "AGENTS.md",
    "PROJECT_STATE.md",
    ".gitignore",
    "pyproject.toml",
    "package.json",
    "apps/api/main.py",
    "docs/PROJECT_VISION.md",
    "docs/PIPELINE_DESIGN.md",
    "docs/STAGE_ROADMAP.md",
    "docs/DATA_MODEL.md",
    "docs/AUDIO_EDITING_STRATEGY.md",
    "docs/TEXT_NORMALIZATION_RULES.md",
    "docs/ASR_STRATEGY.md",
    "docs/ALIGNMENT_STRATEGY.md",
    "docs/LLM_CUT_DECISION_PROTOCOL.md",
    "docs/UI_DESIGN.md",
    "docs/FEEDBACK_LOOP.md",
    "docs/governance/repo_protocol_standard.yaml",
    "docs/governance/file_role_map.yaml",
    "docs/governance/agent_reading_protocol.md",
    "docs/governance/update_log.md",
    "scripts/check_repo.py",
    "scripts/init_data_dirs.py",
    "scripts/agent_gate.py",
    "scripts/auto_advance.py",
    "docs/agent-browser-verification.md",
]

# packages 下每个模块必须有的文件
PACKAGE_MODULES = [
    "audio_core",
    "asr_core",
    "text_core",
    "alignment_core",
    "llm_core",
    "feedback_core",
]

# rounds 目录必须包含 round-00 到 round-11
ROUND_FILES = [
    "round-00-bootstrap.md",
    "round-01-import-manifest.md",
    "round-02-asr-baseline.md",
    "round-03-text-normalization.md",
    "round-04-alignment.md",
    "round-05-llm-cut-decision.md",
    "round-06-review-ui-mvp.md",
    "round-07-waveform-editor.md",
    "round-08-ffmpeg-export.md",
    "round-09-feedback-loop.md",
    "round-10-batch-processing.md",
    "round-11-local-runner.md",
    "round-13-autonomous-real-api-r1.md",
    "round-14-autonomous-dev-loop.md",
]

# .gitignore 必须包含的关键规则片段
GITIGNORE_REQUIRED_PATTERNS = [
    ".env",
    "__pycache__/",
    "node_modules/",
    "data/**",
    "!data/",
    "!data/.gitkeep",
    "*.wav",
    "*.mp3",
    "*.sqlite",
]


def check_directories() -> list[str]:
    """检查关键目录是否存在。"""
    missing: list[str] = []
    for rel in REQUIRED_DIRS:
        if not (ROOT / rel).is_dir():
            missing.append(f"目录缺失: {rel}")
    return missing


def check_files() -> list[str]:
    """检查关键文件是否存在。"""
    missing: list[str] = []
    for rel in REQUIRED_FILES:
        if not (ROOT / rel).is_file():
            missing.append(f"文件缺失: {rel}")
    for mod in PACKAGE_MODULES:
        init_path = f"packages/{mod}/__init__.py"
        readme_path = f"packages/{mod}/README.md"
        if not (ROOT / init_path).is_file():
            missing.append(f"文件缺失: {init_path}")
        if not (ROOT / readme_path).is_file():
            missing.append(f"文件缺失: {readme_path}")
    for rnd in ROUND_FILES:
        rel = f"rounds/{rnd}"
        if not (ROOT / rel).is_file():
            missing.append(f"文件缺失: {rel}")
    return missing


def check_gitignore() -> list[str]:
    """检查 .gitignore 是否包含 data 和音频文件排除规则。"""
    issues: list[str] = []
    gitignore_path = ROOT / ".gitignore"
    if not gitignore_path.is_file():
        return ["文件缺失: .gitignore"]
    content = gitignore_path.read_text(encoding="utf-8")
    for pattern in GITIGNORE_REQUIRED_PATTERNS:
        if pattern not in content:
            issues.append(f".gitignore 缺少规则: {pattern}")
    return issues


def main() -> int:
    """运行全部检查并输出中文结果。"""
    print("=" * 50)
    print("audiobook-cleaner-lab 仓库骨架检查")
    print("=" * 50)

    all_issues: list[str] = []
    all_issues.extend(check_directories())
    all_issues.extend(check_files())
    all_issues.extend(check_gitignore())

    if all_issues:
        print("\n检查未通过，发现以下问题：\n")
        for issue in all_issues:
            print(f"  ✗ {issue}")
        print(f"\n共 {len(all_issues)} 项问题，请修复后重试。")
        return 1

    print("\n✓ 所有关键目录存在")
    print("✓ 所有关键文档存在")
    print("✓ packages 模块骨架完整")
    print("✓ rounds 关键 round 文件齐全")
    print("✓ docs/governance 治理文档齐全")
    print("✓ .gitignore 包含 data 与音频排除规则")
    print("\n仓库骨架检查通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
