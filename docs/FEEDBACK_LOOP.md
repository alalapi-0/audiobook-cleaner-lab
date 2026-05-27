# 反馈闭环（FEEDBACK_LOOP）

模块：`packages/feedback_core`（Round 09）。

## 目标

将用户最终 cut plan 与模型机切建议的差异结构化保存，驱动规则、prompt、padding、confidence 阈值优化——**不做模型微调**（第一阶段）。

## 用户修正如何保存

Review 完成后写入：

1. `user_review.json` — 逐 segment 决策与备注
2. `cut_plan.json` — 最终权威切点
3. `feedback_record.json` — 每条有差异的 segment 一条记录

## model_decision vs user_final_decision

比较维度：

| 维度 | 说明 |
|------|------|
| `action_changed` | keep↔delete 等 |
| `start_shift` / `end_shift` | 切点偏移秒数 |
| `reason_type` 是否一致 | 分类错误统计 |

示例见 `DATA_MODEL.md` 中 `feedback_record.json`。

## 误判统计

按章节/全书聚合：

- LLM delete 被用户改为 keep（**误删风险**，高优先级）
- LLM keep 被用户改为 delete（漏删，较低风险）
- padding 平均偏移量
- uncertain 占比与用户 override 率

输出：`data/logs/feedback_summary_{project_id}.json`

## 如何优化 prompt

- 收集「误删正文」案例 → 追加 few-shot 反例到 `prompts/llm_cut_decision/`
- 强调 matched 高 similarity 不得 delete
- 版本化 prompt 文件，在 feedback 记录中引用 prompt_version

## 如何优化规则

- `filler_detector` 误报 token → 从默认列表移除或加 context 条件
- alignment 阈值调整：误删多则提高 delete 所需 similarity 下限

## 如何优化 padding

- 统计 `end_shift` 均值：若用户常扩大 end → 增大默认 `post_padding`
- 按 `reason_type` 分组的 padding 建议表

## 如何优化 confidence 阈值

- 若 confidence 0.8–0.9 的 delete 常被驳回 → 提高 `never_auto_delete_below_confidence`
- 绘制 confidence vs override 率（Round 09 简单文本报告即可）

## 第一阶段不做模型微调

- 不收集音频训练数据
- 不上传用户素材到云端训练
- 仅 prompt + 规则 + 阈值迭代

## 未来：个性化规则库

可选扩展：

- 每本书 `config/book_rules.yaml`（用户口癖、固定废话模式）
- 从 feedback 自动生成规则候选，用户确认后启用

## 与流水线衔接

```
Round 05 LLM → Round 06 Review → Round 09 feedback
                                      ↓
                    优化 Round 03 规则 / Round 05 prompt / padding 默认值
```

## 当前默认假设

- 单用户数据量有限，统计以人工可读报告为主
- feedback 文件存 `data/reviews/` 与 `data/logs/`
