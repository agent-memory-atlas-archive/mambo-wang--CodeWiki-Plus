---
type: decision
title: "graphiti 调研结论：借鉴分层去重、时间戳软失效、overlay 合并、防御性校验四个工程习惯，不借鉴图数据库全家桶"
tags: ["codewiki", "decision", "minhash"]
metadata:
  date: 2026-09-18
  confidence_level: weak
  task_id: 他山之石
  source_session: "94e1e091eed24b5cbd93153da2656197"
  related_modules: ["knowledge-loop", "notes"]
  severity: medium
  source_ref: "conversations/conv-working_memory_content-The-following-is-the-existing-working-6f15a7.md"
  scene: "他山之石-竞品调研"
status: draft
author: iamwangbao-163-com
generated: { by: codewiki/5.10.1, at: 2026-09-18T06:10:20Z }
stale_after: 2027-09-18
origin: conversation

---

## 背景

对 [getzep/graphiti](https://github.com/getzep/graphiti)（时间感知知识图谱记忆框架，本地 D:/repos/graphiti，HEAD de8eb5b 2026-09-17）做了工作机制调研，完整报告已由用户确认落盘至 docs/graphiti-调研与借鉴分析.md。

## 结论

**值得 CodeWiki 借鉴的四个工程习惯**（与 Team Doctrine 高度同构，低成本高回报）：

1. **确定性快路径 + LLM 兜底的分层去重**（graphiti node_operations.py:627 resolve_extracted_nodes）：语义召回 → 归一化名精确匹配 → MinHash/LSH 模糊匹配（3-gram shingle，Jaccard ≥ 0.9）→ LLM 只裁前三层未决的。短名/低熵名跳过模糊匹配直接升级 LLM（熵门控）。CodeWiki 冲突检测（conflict_case.py）目前纯 LLM 判断，可先加标题/别名归一化精确匹配的零成本快路径。
2. **事实级时间戳软失效**（edges.py:271-282）：旧事实不删除，设 invalid_at/expired_at，新边带 valid_at，历史完整可查。可借鉴给笔记/任务记忆加「失效时间」维度，lint_wiki/query_wiki 按时间过滤过期知识（对 ADR-0009 supersede 机制的扩展方向）。
3. **属性 overlay 合并**（node_operations.py:816-833）：LLM 抽取属性时漏抽/超限丢弃的字段保留旧值（merge_mode='overlay'），只有显式返回的字段才覆盖；返回 {} 会清空属性是 bug 源。note_merge/consolidate_notes 场景直接适用：合并笔记时 LLM 输出缺的 frontmatter 字段应保留原值而非置空。
4. **LLM 输出防御性校验**（node_operations.py:560-601）：所有 LLM 返回的索引 ID 做范围校验——越界剔除+warning、缺失告警、重复忽略，模型输出错乱时流程确定性不崩。蒸馏 submit / 冲突裁决等 LLM JSON 入口应有同款校验：坏字段剔除+日志，而非整体失败。

**明确不借鉴的**：
- 图数据库 + embedding 全家桶：违背 ADR-0001 零依赖单机 Markdown + BM25 的轻量哲学；
- 自动社区摘要：LLM 成本高，且自动改写聚合内容与「入库必经显式确认闸门」核心原则冲突；
- 边级 LLM 矛盾检测的调用密度：CodeWiki 笔记粒度大数量少，照搬会过度调用，取「软失效」语义即可，检测时机留在显式 lint/consolidate。

## 依据

graphiti 源码：摄取流水线 graphiti.py:1043（官方建议异步队列、episode 串行 await）；检索 16 个预置 recipe（search_config_recipes.py）+ RRF/MMR/cross-encoder 等 reranker；社区检测 label propagation 纯 Python 实现。
