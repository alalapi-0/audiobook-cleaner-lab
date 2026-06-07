# 用户视角循环测试最终总结

## 1. 循环次数

共 **2 轮**（Cycle 01 基线测试 → 修复 → Cycle 02 回归验证）。

## 2. 每轮报告列表

- [cycle-01-user-experience-report.md](./cycle-01-user-experience-report.md)
- [cycle-02-user-experience-report.md](./cycle-02-user-experience-report.md)

## 3. 已修复 P0/P1

| 编号 | 标题 | 修复摘要 |
|---|---|---|
| C01-P1-01 | WaveSurfer 初始化失败 | StrictMode 竞态修复；移除 segment 自动播放；友好错误 fallback |
| C01-P1-02 | 缺少项目/章节导航 | App 增加项目/章节下拉、「打开演示章节」、步骤条 |
| C01-P1-03 | UI 缺乏产品感 | 副标题、章节说明、保存/导出引导、样式层级优化 |
| C01-P2-01 | 错误态暴露绝对路径 | API 404 友好化 + `parseApiError` + 错误面板 |
| C01-P2-02 | Web 无导出引导 | 保存成功后显示 `run_export.py` 命令卡片 |
| C01-P2-03 | 127.0.0.1:5173 不可达 | Vite `host: true` |
| C01-P2-04 | 演示音频静音 | seed 新 wav 为 5 秒音调（`--force` 时生效） |

## 4. 当前剩余问题

### P2

- **C02-P2-01**：已存在章节不会自动更新演示 wav，需 `seed_demo_chapter.py --force`
- **C02-P2-02**：`/admin`、`/workbench` 等路由仍 fallback 到 Review 壳，无 NotFound
- **C02-P2-03**：README/部分文档仍优先写 `127.0.0.1:5173`（实测现已双 host 可达）

### P3

- **C02-P3-01**：导入自有素材的 Web 内说明仍较短
- **C02-P3-02**：步骤条「导出」步骤尚无 Web 按钮（CLI 已引导）

### P4

- **C02-P4-01**：前端构建未接入 CI

## 5. 当前用户体验结论

本地 mock 主链路可从首页进入演示章节，完成 Review 保存与波形区操作（无 WaveSurfer 初始化错误），无效项目显示友好错误并可一键返回演示章节，保存后可见 CLI 导出命令。达到个人工具可长期使用的最低标准。

## 6. 当前是否可以停止

是，因为不存在 P0/P1。

## 7. 后续建议

1. 运行 `seed_demo_chapter.py --force` 更新演示音频波形
2. 同步 README 中 Review URL 为 `localhost:5173`（并注明 127.0.0.1 亦可）
3. 为未实现路由增加 NotFound/规划中提示
4. 后续 Round 增加 Web 导出按钮与 CI 前端 build
