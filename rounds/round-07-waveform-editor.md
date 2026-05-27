# Round 07 — 波形时间轴编辑器

## Round 目标

接入 wavesurfer.js，显示删除/保留/不确定区间，支持拖动切点。

## 前置条件

Round 06 Review MVP 可用。

## 主要任务

- 波形加载与区间色块
- 切点拖动写回 cut_plan
- 播放切点前后 2 秒

## 输出文件

- `apps/web/src/components/WaveformEditor.tsx`
- 波形 peaks 缓存 `data/waveforms/`

## 验收标准

- 可拖动调整 delete_range 并保存

## 不做什么

- 不多轨混音

## 下一轮衔接

Round 08：FFmpeg 导出
