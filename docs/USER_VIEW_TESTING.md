# 用户视角测试（User View Testing）

本项目类型：**本地 Web Review 审核台** + **mock 音频文本流水线**。

## 自动化入口

```bash
bash scripts/start_local.sh          # API + Web + demo seed
python3 scripts/user_view_test.py    # URL 探针 + 可选 Playwright
cd apps/web && npm run test          # Playwright E2E
```

报告：`reports/user_view_test_result.json`

## Web / UI 检查清单

| # | 检查项 | 工具 |
|---|--------|------|
| 1 | Review 页加载 | Browser MCP / URL 探针 |
| 2 | 波形编辑器可交互 | 手动 / Playwright |
| 3 | 切点列表与按钮文案 | 截图对比 |
| 4 | 空状态 / NotFoundPage | 导航错误 URL |
| 5 | PlannedPage 占位 | 导航计划路由 |
| 6 | ImportGuide / ExportGuide | 组件可见性 |
| 7 | 窄屏布局 | Browser 设备模式 |
| 8 | console 无 error | chrome-devtools |
| 9 | network 无失败请求 | chrome-devtools |
| 10 | 保存/采纳切点后 UI 反馈 | E2E |

Review URL:

`http://localhost:5173/?project_id=book_001&chapter_id=chapter_001`

## AI 流水线（mock）

| # | 检查项 | 命令 |
|---|--------|------|
| 1 | dry-run 导出 | `run_export.py --dry-run` |
| 2 | mock 生成链路 | `auto_advance.py` |
| 3 | 产物 JSON schema | pytest manifest tests |
| 4 | 真 API 开关默认关 | 无 `.env` Key |
| 5 | 失败样本 | 检查 logs / reports |

## 音频/媒体

| # | 检查项 |
|---|--------|
| 1 | 输入 wav 只读 |
| 2 | 导出格式与元数据 |
| 3 | FFmpeg dry-run 不覆盖原文件 |
| 4 | 预览页波形加载 |

## 翻译/章节（本书项目）

| # | 检查项 |
|---|--------|
| 1 | 章节 manifest 完整性 |
| 2 | 原文与 ASR 对齐结果可读 |
| 3 | 术语/格式一致性（normalize 规则） |
| 4 | 断点续跑 batch_process |

## 不可自动化时

记录 `BLOCKED_ENV`：服务未启动、MCP 不可用 → 在报告中说明 fallback（CLI Playwright 或人工）。

## 相关文档

- [testing/BROWSER_TESTING.md](testing/BROWSER_TESTING.md)
- [testing/USER_PERSPECTIVE_TESTING.md](testing/USER_PERSPECTIVE_TESTING.md)
- [cursor_browser_ui_runbook.md](cursor_browser_ui_runbook.md)
