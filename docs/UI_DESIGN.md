# UI 设计（UI_DESIGN）

Round 00 仅规划，Round 06–07 实现。技术栈：React + Vite + TypeScript + wavesurfer.js。

## 页面结构

### 1. 项目选择页

- 列出 `project_manifest` 中的书籍
- 新建项目（书名、语言）
- 显示每书章节数与整体进度

### 2. 章节选择页

- 章节列表：标题、status、时长
- 快捷入口：ASR / 对齐 / Review / 导出
- 批处理队列状态（Round 10）

### 3. Review 页面（核心）

布局建议三栏 + 底栏波形：

```
┌─────────────┬─────────────┬─────────────┐
│  原文文本区  │  ASR 文本区  │  模型建议区  │
│  (高亮对齐)  │  (segment)  │ keep/del/?  │
├─────────────┴─────────────┴─────────────┤
│  音频播放器 + 波形时间轴 + 区间色块        │
└─────────────────────────────────────────┘
```

#### 原文文本区

- 显示 normalized 原文
- 高亮当前选中 segment 对应 source_range
- 滚动同步

#### ASR 文本区

- 按 segment 列表展示
- 点击 segment 跳转音频时间
- 显示 alignment status 色标

#### 模型建议区

- 每条 decision：action、reason、confidence
- 按钮：确认 / 驳回 / 标记不确定
- **uncertain** 项醒目提示需人工试听

#### 音频播放器

- 播放/暂停/seek
- **播放切点前后 2 秒** 按钮（便于判断 padding）

#### 波形时间轴（Round 07）

- wavesurfer.js 渲染
- **删除区间**：红色半透明
- **保留区间**：绿色底
- **不确定区间**：黄色虚线
- **切点拖动**：调整 delete_range 边界

### 4. 快捷键（规划）

| 快捷键 | 动作 |
|--------|------|
| `K` | 确认当前建议（keep/delete） |
| `R` | 驳回模型建议 |
| `U` | 标记 uncertain |
| `Space` | 播放/暂停 |
| `←/→` | 上一/下一 segment |
| `Ctrl+S` | 保存 user_review |

### 5. 保存与导出

- **保存人工校正** → `user_review.json` + 更新 `cut_plan.json`
- **导出按钮** → 触发后端 FFmpeg（Round 08），显示 dry-run 选项

## 状态色规范

| 状态 | 颜色 |
|------|------|
| matched / keep | 绿 |
| delete 建议 | 红 |
| uncertain | 黄 |
| missing | 灰 |

## 非目标（Round 06–07）

- 多轨编辑、音效、配乐
- 用户登录与权限
- 移动端适配（先桌面）

## 当前默认假设

- 单章 Review 页面加载 < 10k segment 可接受
- 音频流式加载，不全量读入内存
