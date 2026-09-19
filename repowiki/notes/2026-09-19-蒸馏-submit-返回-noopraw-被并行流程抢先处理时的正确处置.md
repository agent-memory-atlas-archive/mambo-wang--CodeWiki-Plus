---
type: pitfall
title: "蒸馏 submit 返回 noop：raw 被并行流程抢先处理时的正确处置"
tags: ["pitfall"]
metadata:
  date: 2026-09-19
  confidence_level: weak
  task_id: 他山之石
  source_session: "c07baaa505eb4d5e8a426636266c63a0"
  related_modules: ["knowledge-loop"]
  severity: medium
  source_ref: "conversations/conv-working_memory_content-The-following-is-the-existing-working-788cb5.md"
  scene: "补蒸馏 worker 执行"
status: draft
author: iamwangbao-163-com
generated: { by: codewiki/5.10.1, at: 2026-09-19T01:15:17Z }
stale_after: 2027-03-18
origin: conversation

---

## Background

补蒸馏 worker（Mode C）在 prepare 与 submit 之间，目标 raw 被另一条并行蒸馏流程抢先处理并归档到 `repowiki/conversations/`，submit 返回 noop（「No pending conversations bound to task」），worker 已完成的提取结果无法经 submit 落盘。

## 正确做法

1. **不绕过 noop 强行提交**——noop 是确定性簿记在保护归档一致性，绕过 dispatch 直连 handler 会破坏状态机。
2. 把提取结果暂存到 `repowiki/raw/.distill-<conversation_id>.json`（形状 `{conversation_id: {notes, memories}}`），随汇报交给主 Agent。
3. 主 Agent 按「子代理自报结果须独立复核」原则读暂存文件核实后，经评审通道 `ingest_note(status=draft)` 补录，不跳过确认闸门。
4. 补录完成后**手动删除暂存文件**——submit noop 时工具不会自动删除 `.distill-*.json`，会留下垃圾文件。

## Root cause

蒸馏流程无全局锁，prepare 返回的积压清单只是时点快照；同一 raw 可被会话内并行流程（如收尾采集后立即触发的主流程蒸馏）同时处理。并行提取的覆盖面可能与本 worker 不同（本次并行流程只提取了 2 条，worker 的 3 条未被覆盖），所以 noop 不代表提取作废，需人工比对覆盖面。

## 适用范围

任何 Mode C 补蒸馏 worker 遇到 submit noop 时；也适用于评估「是否需要给 distill_conversation 加任务级锁」的讨论基线。
