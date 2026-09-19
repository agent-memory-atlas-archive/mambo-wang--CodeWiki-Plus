---
type: decision
title: "distill/聚合 prompt 吸收 hindsight 两条合并规则：每条 op 必带 reason + NO COMPUTATION"
tags: ["decision"]
metadata:
  date: 2026-09-19
  confidence_level: weak
  task_id: 他山之石
  related_modules: ["knowledge-loop"]
  severity: medium
  source_ref: "raw\\conv-https-github.com-vectorize-io-hindsight-调研项目.md"
  scene: "他山之石竞品调研（hindsight）"
status: draft
author: iamwangbao-163-com
generated: { by: codewiki/5.10.1, at: 2026-09-19T14:53:38Z }
stale_after: 2027-09-19
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
