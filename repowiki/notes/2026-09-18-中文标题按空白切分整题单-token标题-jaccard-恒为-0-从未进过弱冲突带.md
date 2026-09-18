---
type: pitfall
title: 中文标题按空白切分整题单 token，标题 Jaccard 恒为 0 从未进过弱冲突带
tags:
- pitfall
metadata:
  date: 2026-09-18
  confidence_level: strong
  task_id: 他山之石
  related_modules:
  - knowledge_loop
  - retrieval
  verification:
    commit_ref: 858f6eb
    test_ref: tests/test_distill_defensive.py
status: stable
author: iamwangbao-163-com
generated:
  by: codewiki/5.10.1
  at: 2026-09-18 09:37:56+00:00
stale_after: '2027-03-17'
verified:
- by: human:wangbao
  at: '2026-09-18T09:47:10Z'
---

## 背景

graphiti 调研报告曾断言：「发版本」vs「发版本流程」的标题 Jaccard = 0.5、会落入 0.35~0.6 弱冲突带交 agent 裁决。grill Round 1 实施前的代码核对证伪了这一判断。

## 现象

`_title_tokens`（codewiki/mcp/tools/distill_conversation.py:460-462）按空白/下划线/连字符切分标题。中文标题没有空格，整个标题成为一个 token——任意两个不同的纯中文标题 token 集合交集为空，Jaccard 恒为 0。也就是说：纯中文标题从未进过标题 Jaccard 弱冲突带，中文笔记的冲突检测实际只靠 BM25 兜底。

## 正确做法

让 `_title_tokens` 复用 `retrieval.tokenize`（retrieval kernel 已有的 jieba 分词），中文近重复标题才能进入 Jaccard 带。ADR-0011 已实施（distill_conversation.py:460-470）。

## 根因

按空白切分的隐含假设只对以空格分词的西文成立；对 CJK 文本，切分层缺失等价于相似度信号整体缺失。更一般的教训：调研报告里「想当然算出的相似度数值」必须经代码核对才能当事实引用——本次 grill 正是靠实施前核对抓出了这个错误（Doctrine：直觉根因须被数据证伪）。
