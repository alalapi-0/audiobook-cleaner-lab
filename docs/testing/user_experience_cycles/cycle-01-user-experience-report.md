# 用户视角循环测试报告 Cycle 01

## 1. 测试时间

2026-06-07（Cycle 01 基线复测）

## 2. 当前 Git 信息

- branch: main
- commit: 66a65e8
- working tree: clean（测试开始时）

## 3. 本轮测试范围

UP-01 至 UP-08 全路径；重点复测 WaveformEditor、项目导航、错误态、UI 美观度。

## 4. 本轮启动方式

- API: `.venv/bin/python -m uvicorn apps.api.main:app --host 127.0.0.1 --port 8000`
- Web: `cd apps/web && npm run dev`
- Browser tool: cursor-ide-browser MCP
- 测试 URL: `http://localhost:5173/`、`/?project_id=book_001&chapter_id=chapter_001`、`/?project_id=nonexistent&chapter_id=chapter_001`

## 5. 自动化命令结果

| 命令 | 结果 | 备注 |
|---|---|---|
| `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'` | passed | 31 tests |
| `cd apps/web && npm run build` | passed | |
| `cd apps/web && npm run test` | passed | 5 smoke tests |
| `.venv/bin/python scripts/agent_gate.py` | passed | |

## 6. 用户路径测试结果

| 用户路径 | 结果 | 问题编号 |
|---|---|---|
| UP-01 首次访问 | 部分通过 | C01-P1-02, C01-P3-01 |
| UP-02 核心 Review 闭环 | 通过 | — |
| UP-03 波形微调 | 失败 | C01-P1-01 |
| UP-04 错误恢复 | 失败 | C01-P2-01 |
| UP-05 CLI 导入到导出 | 通过 | C01-P2-02 |
| UP-06 环境与启动 | 通过 | C01-P2-03 |
| UP-07 小屏幕 | 部分通过 | — |
| UP-08 视觉美观 | 部分通过 | C01-P1-03 |

## 7. UI 美观与可用性评分

- 首屏理解度：3/5（缺工具说明与步骤引导）
- 信息层级：3/5
- 核心操作可见性：4/5
- 波形区可用性：1/5（初始化失败）
- 错误态友好度：2/5（暴露绝对路径与 JSON）
- 小屏幕可用性：4/5
- 整体美观度：3/5
- 是否达到个人工具可长期使用标准：否

## 8. 问题清单

### P0

| 编号 | 标题 | 复现 | 影响 | 修复建议 |
|---|---|---|---|---|
| — | — | — | — | — |

### P1

| 编号 | 标题 | 复现 | 影响 | 修复建议 |
|---|---|---|---|---|
| C01-P1-01 | WaveSurfer 初始化失败 | Review 页底部显示「波形加载失败: WaveSurfer is not initialized」 | 波形、播放、拖动切点不可用 | 修复 StrictMode 竞态；移除自动播放；重置 ready 状态 |
| C01-P1-02 | 缺少项目/章节导航 | 打开 `/` 无选择器，新用户不知 project_id 来源 | 必须手写 URL 参数 | 增加项目/章节下拉与「打开演示章节」 |
| C01-P1-03 | UI 缺乏产品感 | 页面像 debug 壳，无副标题与步骤条 | 降低信任感，难以理解下一步 | 增加副标题、步骤条、章节说明卡片 |

### P2

| 编号 | 标题 | 复现 | 影响 | 修复建议 |
|---|---|---|---|---|
| C01-P2-01 | 错误态暴露绝对路径 | `nonexistent` 项目显示 `/Users/.../chapter_manifest.json` | 泄露本机路径 | API/前端友好化 404 |
| C01-P2-02 | Web 无导出引导 | 保存后无下一步说明 | 用户不知 CLI 导出 | 保存成功后显示 run_export 命令 |
| C01-P2-03 | 127.0.0.1:5173 不可达 | README 写 127.0.0.1，Vite 仅 localhost | 文档与实测不一致 | Vite `host: true` |
| C01-P2-04 | 演示音频为 1 秒静音 | seed 生成静音 wav | 波形体验差 | 生成带音调的 5 秒演示 wav |

### P3

| 编号 | 标题 | 复现 | 影响 | 修复建议 |
|---|---|---|---|---|
| C01-P3-01 | 缺导入自己的音频说明 | 首页无导入指引 | 新用户卡住 | 增加简短 CLI 导入说明 |
| C01-P3-02 | 未知路由无 NotFound | `/admin` 等同 Review 壳 | 边缘路径困惑 | 增加未实现提示 |

### P4

| 编号 | 标题 | 复现 | 影响 | 修复建议 |
|---|---|---|---|---|
| C01-P4-01 | 无 CI 前端构建 | 本地 npm build | 工程化 | 后续 CI |

## 9. 是否需要进入修复轮

- has_p0: false
- has_p1: true
- decision: continue_fix

## 10. 本轮结论

核心 Review 保存闭环可用，但波形区 P1 阻塞切点微调体验；导航与 UI 产品感不足判为 P1。错误态与导出引导为 P2，本轮修复轮将优先处理全部 P1 及同源 P2。

## 11. 下一步

立即进入修复轮：WaveformEditor、项目导航、错误态友好化、导出引导、UI 层级优化；补充 Playwright UX 回归用例。
