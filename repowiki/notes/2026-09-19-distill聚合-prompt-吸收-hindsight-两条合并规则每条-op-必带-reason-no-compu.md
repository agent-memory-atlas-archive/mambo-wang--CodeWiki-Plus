---
type: decision
title: distill/聚合 prompt 吸收 hindsight 两条合并规则：每条 op 必带 reason + NO COMPUTATION
tags:
- decision
metadata:
  date: 2026-09-19
  confidence_level: shadow
  task_id: 他山之石
  related_modules:
  - knowledge-loop
  severity: medium
  source_ref: conversations/conv-https-github.com-vectorize-io-hindsight-调研项目.md
  scene: 他山之石竞品调研（hindsight）
  verification:
    commit_ref: ADR-0012
    test_ref: tests/test_distill_p1.py::test_prompt_contains_p1_disciplines_and_fields
status: deprecated
author: iamwangbao-163-com
generated:
  by: codewiki/5.10.1
  at: 2026-09-19 14:53:38+00:00
stale_after: '2027-09-20'
origin: conversation
verified:
- by: human:wangbao
  at: '2026-09-20T01:40:39Z'
reject_reason: consolidated into 竞品调研与借鉴方法 与 对话蒸馏管线与raw暂存区
---

## 背景

hindsight consolidation prompt 共九条合并规则，调研处置（报告 docs/hindsight-调研与借鉴分析.md，结论已直写任务「他山之石」记忆）从中吸收两条进本仓 distill/聚合 prompt 设计，其余规则未吸收。

## 决策

吸收的两条规则：

1. **每条合并 op 必带 reason**——合并/更新/删除操作必须给出可审计的依据，不允许无理由改写；
2. **NO COMPUTATION**——不做算术推断，只记录对话中明说的数字，防止蒸馏环节凭空计算产生假数据。

## 理由

两条规则与本仓「工具做确定性簿记、推理决策在调用方与用户手里」的架构前提一致，改造成本低、直接提升蒸馏与聚合产出的可审计性。未吸收的规则（Mission 优先于处理规则、语言保持规则等）前提与本仓不符或已有等价实现。

## 适用范围

调整 `distill_conversation` 提取规范或知识聚合（consolidation）prompt 时参考；hindsight 其余机制处置见调研报告（absorbed 2 / deferred 2 / excluded 8）。

## 落地（2026-09-19 已实施）

经 grill 拷问定案（ADR-0012）：两条规则合并为一条第 6 条纪律写入 `_DISTILL_SYSTEM`（codewiki/mcp/tools/distill_conversation.py，"Reasoned and literal"），聚合侧不动（dispositions 已强制 reason），tests/test_distill_p1.py 补断言，全量 1169 passed。absorbed 语义定为「必须有可指认的落点，否则降级 deferred」。
