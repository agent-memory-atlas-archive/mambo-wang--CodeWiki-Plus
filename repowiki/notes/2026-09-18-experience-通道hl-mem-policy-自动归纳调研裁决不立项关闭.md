---
type: decision
title: Experience 通道（HL-Mem Policy 自动归纳）调研裁决：不立项关闭
tags:
- decision
metadata:
  date: 2026-09-18
  confidence_level: weak
  task_id: 他山之石
  source_session: 94e1e091eed24b5cbd93153da2656197
  related_modules:
  - task_memory
  - knowledge_loop
  severity: medium
  source_ref: conversations/conv-working_memory_content-The-following-is-the-existing-working-3b1d9b.md
  scene: 他山之石竞品调研：HL-Mem 遗留候选裁决
status: stable
author: iamwangbao-163-com
generated:
  by: codewiki/5.10.1
  at: 2026-09-18 09:20:39+00:00
stale_after: '2027-09-19'
origin: conversation
verified:
- by: human:wangbao
  at: '2026-09-18T09:47:10Z'
- by: human:wangbao
  at: '2026-09-19T01:21:43Z'
---

## 背景

HL-Mem 调研（2026-09-12，`docs/HL-Mem-调研与借鉴分析.md`）遗留一个未排期候选：是否借鉴 HL-Mem 的 Experience 通道——把 Agent 执行轨迹自动归纳成可复用 Policy。2026-09-18 实读 `D:\repos\hl_mem` 源码后裁决：**关闭该候选，不立项**。

## HL-Mem Experience 通道机制（实读代码结论）

一条「轨迹 → 策略」自动归纳流水线：
1. **Episode/Trace 记录**：Agent 每次执行记录 goal、状态、reward（0~1）、前 3 个 action 序列（`storage/experience.py:88-119`）
2. **策略归纳**：每日 cron 聚类近期成功 Episode（reward ≥ 0.5），按 `(namespace, task_type, 前3-action前缀)` 聚簇，簇 ≥ min_support(2) 时归纳出 Policy（`workers/induce_policies.py:15-75`）
3. **策略生命周期**：`candidate → active → retired` 状态机，使用结果回写 success_count/failure_count，连续失败 ≥3 自动退休，reliability = 成功率（`storage/experience.py:546-566`）
4. **检索注入**：按 `0.40×text_match + 0.35×reliability + 0.15×usefulness + 0.10×recency` 排序注入 Context Packet（`recall/procedure_pipeline.py:133-146`）

## 不立项的理由

1. **前提条件不具备——没有 reward 信号**。整条流水线建立在「reward ≥ 0.5 的成功 Episode」筛选前提上；CodeWiki 蒸馏输入是对话 transcript，没有结构化成败判定。补这个前提需宿主 Agent 提供 Episode 记录 + reward 标注体系，不是 CodeWiki 单方面能做的。
2. **与主动沉淀协议职责重叠**。ACTIVE-SETTLE 协议已覆盖「从会话提取可复用经验」（停顿点判据 → add_task_memory 直写 / ingest_note 落草稿）；Policy 自动归纳是同一职责的自动版，而 Doctrine 明确「不自动蒸馏/聚合：触发永远显式」。
3. **归纳粒度不匹配**。Policy 本质是「前 3 个 action 的序列模板」，对工具调用密集的自动化 Agent 有意义；CodeWiki 的知识工作场景（决策/教训/架构事实）粒度太粗。已有的场景块（wiki/scenarios/）就是人工策展的 Policy，质量远高于自动聚类产物。
4. **成本收益不匹配**。HL-Mem 为此建了 4 张表（episodes/traces/policies/evidence_links）+ 状态机 + cron worker + deferred task 兜底；CodeWiki 蒸馏笔记已含经验类型（lesson/pitfall）且经确认闸门保证质量。

## 留意的两个小点（不立项，记入备忘）

- **reliability 加权检索**：CodeWiki 的 `adopted_count` 已是类似信号（采纳权重 2 倍），方向一致，无需新做。
- **连续失败自动退休**：与 ADR-0009「受控降状态」语义同构；若未来 lint_wiki 发现「反复被引用但总被纠正」的笔记，可参考其 consecutive_failures 机制。

## 重启信号（满足任一再评估）

1. 宿主 Agent 提供结构化 reward/trace；
2. 场景块数量增长到人工策展吃力。
