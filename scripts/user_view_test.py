#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用户视角测试清单 — 本仓库为本地 Web Review 审核台 + mock 流水线。

不启动真实付费 API；可选检查本地服务是否可达。
"""

from __future__ import annotations

import json
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORT_PATH = ROOT / "reports" / "user_view_test_result.json"

CHECKLIST = [
    {
        "id": "review_page_loads",
        "description": "Review 页可打开（需 API + Web 运行）",
        "url": "http://127.0.0.1:5173/?project_id=book_001&chapter_id=chapter_001",
    },
    {
        "id": "api_health",
        "description": "FastAPI 可访问",
        "url": "http://127.0.0.1:8000/docs",
    },
]


def probe_url(url: str, timeout: float = 3.0) -> dict:
    """HTTP GET 探针（只读）。"""
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return {"url": url, "ok": resp.status < 400, "status": resp.status}
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return {"url": url, "ok": False, "error": str(exc)}


def run_playwright_if_available() -> dict:
    """若 node_modules 存在则运行 Playwright 测试。"""
    web = ROOT / "apps" / "web"
    if not (web / "node_modules").is_dir():
        return {"ran": False, "reason": "apps/web/node_modules missing — run npm install"}
    result = subprocess.run(
        ["npm", "run", "test"],
        cwd=web,
        capture_output=True,
        text=True,
        timeout=300,
    )
    return {
        "ran": True,
        "exit_code": result.returncode,
        "summary": (result.stdout or result.stderr or "")[-500:],
    }


def main() -> int:
    """执行用户视角检查并写入报告。"""
    timestamp = datetime.now(timezone.utc).isoformat()
    url_results = [probe_url(c["url"]) for c in CHECKLIST]
    playwright = run_playwright_if_available()

    report = {
        "timestamp": timestamp,
        "project_type": "local_web_review + mock_audio_pipeline",
        "manual_checklist": [
            "波形编辑器可交互",
            "切点列表与按钮文案可读",
            "空状态 / 404 页（NotFoundPage）",
            "console 无 error（需 Browser MCP 或手动）",
            "network 无失败请求（需 Browser MCP 或手动）",
            "窄屏布局（需 Browser MCP 或手动）",
        ],
        "url_probes": url_results,
        "playwright": playwright,
        "docs": "docs/USER_VIEW_TESTING.md",
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    services_up = all(r.get("ok") for r in url_results)
    pw_ok = not playwright.get("ran") or playwright.get("exit_code") == 0

    print("=" * 50)
    print("用户视角测试")
    print("=" * 50)
    for r in url_results:
        status = "✓" if r.get("ok") else "✗ (服务未启动或不可达)"
        print(f"  {status} {r['url']}")
    if playwright.get("ran"):
        print(f"  Playwright exit {playwright['exit_code']}")
    else:
        print(f"  Playwright: {playwright.get('reason', 'skipped')}")
    print(f"\n报告: {REPORT_PATH.relative_to(ROOT)}")

    if not services_up:
        print("\n提示: 先运行 bash scripts/start_local.sh")
        return 2
    return 0 if pw_ok else 1


if __name__ == "__main__":
    sys.exit(main())
