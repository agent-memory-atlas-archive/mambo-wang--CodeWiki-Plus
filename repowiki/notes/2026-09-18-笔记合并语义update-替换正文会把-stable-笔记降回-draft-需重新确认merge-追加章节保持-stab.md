---
type: pitfall
title: 笔记合并语义：update 替换正文会把 stable 笔记降回 draft 需重新确认，merge 追加章节保持 stable
tags:
- pitfall
metadata:
  date: 2026-09-18
  confidence_level: weak
  task_id: 他山之石
  source_session: 94e1e091eed24b5cbd93153da2656197
  related_modules:
  - note_consolidation
  - distill_conversation
  severity: medium
  source_ref: conversations/conv-working_memory_content-The-following-is-the-existing-working-3c9e3c.md
  scene: 蒸馏草稿批量确认（14 条）
status: stable
author: iamwangbao-163-com
generated:
  by: codewiki/5.10.1
  at: 2026-09-18 06:47:59+00:00
stale_after: '2027-03-17'
origin: conversation
verified:
- by: human:wangbao
  at: '2026-09-18T07:13:49Z'
---

## 背景

确认蒸馏 worker 产出的 14 条草稿时发现：worker 报告的「合并/更新」条目实际分两种语义，确认流程处理方式不同，混为一谈会漏确认或重复确认。

## 正确做法

- **`dedup_action=update`（替换正文）**：被替换的 stable 笔记会**降回 draft 状态**，必须重新 `confirm_note` 才恢复 stable。实例：`2026-09-16-补蒸馏改为阻塞式…` 被异步化新决策替换正文后回到 draft，已重新确认。
- **`dedup_action=merge`（追加章节）**：既有 stable 笔记**保持 stable 不变**，无需再确认。实例：`2026-09-08-双语语料与模板的一致性…`、`2026-09-11-AGENTS.md-约-79%…`、`2026-08-23-distill-worker-subagent…` 三条合并后仍 stable。
- 复核 worker 自报结果时按此语义分流检查：update 的查状态是否回 draft，merge 的查章节是否追加成功。

## 根因

update 语义上是「内容被推翻重写」，等于新知识，须重走确认闸门；merge 是「既有知识扩写」，原确认仍有效。这与 Doctrine「确认闸门对等」一致：凡实质变更落盘知识都重新过闸。

## 适用范围

蒸馏 submit 触发 conflicts_pending 后的裁决轮、consolidate_notes 聚合、以及任何对既有笔记做 update/merge 的场景。
