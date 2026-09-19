---
type: decision
title: "supermemory 调研处置：12 候选 0 立即落地，reject 可见性经代码验证已等价"
tags: ["decision"]
aliases: ["supermemory 借鉴处置", "deprecated 降权三层设计", "declined 即 forgotten 等价验证"]
metadata:
  date: 2026-09-19
  confidence_level: weak
  task_id: 他山之石
  related_modules: ["retrieval", "note_query", "distill_conversation"]
status: draft
author: iamwangbao-163-com
generated: { by: codewiki/5.10.1, at: 2026-09-19T14:33:32Z }
stale_after: 2027-09-19
---

## 背景

supermemory（HEAD 57b430b，2026-09-18）调研后用户追问「有值得借鉴落地的吗」，经 grill 模式逐项拷问定案。调研报告：docs/supermemory-调研与借鉴分析.md。

## 结论

**无立即落地项。** 12 项候选处置：6 excluded（已有等价）、3 deferred（挂线）、2 归任务参考、1 absorbed（维持挂起）。

关键验证：supermemory「declined 即 forgotten」（驳回即从检索完全移除）语义，本仓已完全等价，且是更精细的三层设计：

1. **handler 层跳过**：三个知识服务读路径（默认 BM25 note_query.py:1030、check 预检 note_query.py:465、by_file 时间线 note_query.py:672）全部跳过 deprecated 笔记；
2. **索引层降权**：retrieval.py:485 对 deprecated -0.35 降权，把死知识压出 top-N 槽位区间（handler 过滤发生在 top-N 之后，不降权会浪费结果槽位）；
3. **去重层豁免**：distill_conversation.py:678 传 apply_authority=False，蒸馏冲突检测需看见已驳回笔记的全相似度，新草稿与已驳回笔记相似不该被降权掩盖。

## 根因

曾误判「deprecated -0.35 降权是死代码」（handler 已跳过，降权永不生效）。代码核对证伪：降权作用于索引排序层，在 handler 过滤之前就把 deprecated 压出槽位，是槽位效率设计而非语义设计。教训：判断某权重是否死代码前，先确认它作用在哪一层、过滤发生在排序前还是后。

## deferred 项（挂线不立项）

- derives 推断关系 + isLatest 时间真值：知识形态不同（supermemory 记用户事实需时间真值，本仓记工程经验走 reject/supersede 已够），挂知识飞轮主线；
- SMFS 文件系统哲学：归「Cli能力」任务；
- MemoryBench 基准：归质量量化主线（同根信号第三次出现）。

## 适用范围

未来评估记忆类竞品借鉴时，先过三问：本仓已有等价实现？前提成立？成本配得上收益？同构验证（确认本仓设计正确）也是调研收益。
