# 文本规范化规则（TEXT_NORMALIZATION_RULES）

## 模块划分

| 组件 | 职责 |
|------|------|
| `source_text_normalizer` | 清洗用户提供的正确原文 |
| `asr_text_normalizer` | 清洗 ASR segment 文本 |
| `filler_detector` | 标记语气词/废话**候选**，不自动删除 |

实现模块：`packages/text_core`（Round 03）。

---

## source_text_normalizer

### 标点统一

- 中文正文使用全角标点（。，！？；：）
- 英文专有名词、数字单位保留半角
- 省略号统一为「……」

### 空格清理

- 去除行首行尾空白
- 合并连续空格为单个（中文一般无词间空格）
- 保留段落换行（`\n\n`）

### 全角半角

- 数字、字母在纯中文语境可统一半角（可配置）
- 引号统一为「」或 ""（按项目配置）

### 数字处理

- 阿拉伯数字与中文数字**不强制互转**（避免改变语义）
- 记录原始形式，对齐时允许 fuzzy 匹配

### 章节标题处理

- 识别「第X章」等标题行，标记为 `heading` 类型
- 标题不参与 filler 检测

### 引号和括号

- 统一括号形态（）【】
- 不删除括号内合法正文

---

## asr_text_normalizer

在 source 规则基础上：

- 去除 ASR 常见口语标点噪声
- 可选去除 segment 内多余空格
- **保留** segment 与 `segment_id` 的映射

---

## filler_detector

识别候选（**不自动删除**）：

- 嗯、啊、呃、那个、就是、然后（句首孤立出现时）
- 明显 off-script 自言自语模式

输出示例：

```json
{
  "token": "嗯",
  "type": "filler",
  "auto_delete": false,
  "note": "候选，需结合 alignment 与 LLM 判断"
}
```

### 不要粗暴删除所有「嗯、啊、就是、然后」

这些词可能是：

- 正文对话中的合法用词
- 作者有意保留的口语风格

因此 **filler_detector 只标记**，最终 delete 由 alignment + LLM + 人工决定。

---

## 废话词处理原则

| 阶段 | 行为 |
|------|------|
| 正则/规则 | 仅 `extra_candidate` 或 filler 候选 |
| LLM | 结合原文上下文判断 delete/keep/uncertain |
| 人工 | 最终权威 |

---

## 规则配置

Round 03 起支持 `config/text_normalization.yaml`（不进 Git  secrets），含：

- `punctuation_mode`
- `filler_tokens[]`
- `heading_patterns[]`

---

## 风险

- 过度清洗导致 alignment 相似度虚高或虚低
- 误标 filler 导致 LLM 倾向 delete

缓解：保守标记 + uncertain 人工确认 + feedback 优化规则。
