---
type: decision
title: "graphiti 借鉴落地闭环：C+E 拍板实施为 ADR-0011，B 缓做 A 不做"
tags: ["decision"]
metadata:
  date: 2026-09-18
  confidence_level: weak
  task_id: 他山之石
  related_modules: ["knowledge_loop", "notes"]
status: draft
author: iamwangbao-163-com
generated: { by: codewiki/5.10.1, at: 2026-09-18T09:37:45Z }
stale_after: 2027-09-18
---

## 背景

graphiti 调研笔记的「落地对照基线」章节列出 4 个候选（C 防御性校验、E 短标题门控、B 检索 recipe 预设、A 退役时间维度），当时标注「尚未拍板，实施前须确认」。本节记录后续拍板与实施结果，修正该章节的待定状态。

## 决策

用户确认「全部按推荐」：

- **C（LLM 输出防御性校验）必做**：`_parse_llm_notes` 解析失败不再返回 `[]` 当 no_knowledge（那会把 raw 原料永久删除），改为 raw 保留、`status=parse_failed`、响应显式 `parse_error` 字段；失败原因写入 raw frontmatter 的 `parse_error` 键（Q6(b) 口径：信息随文件走，显式优于缓存，下轮 worker 无需重读全文即知失败原因）；单条 note 缺 title/content 剔除并记 `invalid_note`，不静默。
- **E（中文标题分词）值得做**：`_title_tokens` 复用 `retrieval.tokenize`（jieba），中文近重复标题首次进入 Jaccard 弱冲突带。修法是复用既有分词器（单点收敛），而非引入 graphiti 式字符熵门控（未经验证的公式不引入）。
- **B（检索 recipe 预设化）缓做**：现有 mode（check/full/by_file）够用，等调用方抱怨参数面再做。
- **A（退役时间维度）不做**：ADR-0009 刚落地一天，退役语义还没跑出真实痛点，先让子弹飞。
- **实施归属**：归「产品维护」任务线当普通 bugfix；调研任务（他山之石）只出报告，混进实施会让任务记忆变成实施日志。

## 结果

ADR-0011 落盘 `docs/adr/0011-distill-defensive-validation-and-cjk-title-tokens.md`（含 Round 2 增补章节）；新增 `tests/test_distill_defensive.py`；全量 1165 passed, 2 skipped 无回归；已提交推送（774dab3..858f6eb）。这是「他山之石」任务里第一个走完全程（调研 → grill → ADR → 实施 → 测试）的借鉴。
