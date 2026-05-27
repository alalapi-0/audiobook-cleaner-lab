# audio_core

## 模块职责

负责音频层面的非破坏式处理：预处理、波形元数据、切点区间验证，以及基于 `cut_plan.json` 的 FFmpeg 导出。

## 当前 Round 状态

**Round 00**：仅占位，无实现代码。

## 未来要实现

- 音频格式探测与归一化参数建议
- 波形峰值缓存（供前端 wavesurfer.js 使用）
- `cut_plan.json` → FFmpeg filter_complex 生成
- dry-run 模式：只输出命令与区间，不执行
- 正式导出：生成 `data/exports/` 下干净音频

## 输入 / 输出

| 阶段 | 输入 | 输出 |
|------|------|------|
| 预处理 | 原始 WAV/MP3 路径 | 预处理报告 JSON |
| 波形 | 音频路径 | `data/waveforms/*.json` |
| 导出 | `cut_plan.json` | 干净 MP3/WAV + `export_report.json` |

## 与其他模块的关系

- 依赖 `asr_core` 的时间戳区间做切点边界校验
- 接收 `llm_core` / 用户 review 汇总的 `cut_plan.json`
- 为 `feedback_core` 提供导出前后时长对比数据
