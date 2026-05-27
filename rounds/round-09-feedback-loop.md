# Round 09 — 反馈优化闭环

## Round 目标

比较 model_decision 与 user_final_decision，生成 `feedback_record.json` 与统计报告。

## 前置条件

Round 06–08 产生 review 与 cut_plan。

## 主要任务

- `packages/feedback_core` 实现 diff 与 lesson 生成
- 误删/ padding 偏移统计
- 文本报告输出

## 输出文件

- `feedback_record.json`
- `data/logs/feedback_summary_*.json`

## 验收标准

- 示例 diff 生成 lesson 字段
- 汇总误删次数

## 不做什么

- 不做模型微调

## 下一轮衔接

Round 10：批处理
