---
type: lesson
title: 任务记忆中的候选状态标注可能滞后于笔记实际生命周期，裁决前以 frontmatter 实际状态为准
tags:
- codebuddy
- lesson
metadata:
  date: 2026-09-18
  confidence_level: weak
  task_id: 他山之石
  source_session: 94e1e091eed24b5cbd93153da2656197
  related_modules:
  - task_memory
  severity: medium
  source_ref: conversations/conv-working_memory_content-The-following-is-the-existing-working-3b1d9b.md
  scene: 他山之石任务遗留待办清理
status: stable
author: iamwangbao-163-com
generated:
  by: codewiki/5.10.1
  at: 2026-09-18 09:18:56+00:00
stale_after: '2027-03-17'
origin: conversation
verified:
- by: human:wangbao
  at: '2026-09-18T09:47:19Z'
---

## 背景

「他山之石」任务记忆中长期标注「旧 draft『在 CodeBuddy 使用跨 Agent 技能』保留待定未裁决」。2026-09-18 处理遗留待办时核查发现：该笔记实际已走完生命周期（stable → 合并进 `wiki/scenarios/IDE-Hook采集链路方法.md` → deprecated 退役），任务记忆里的标注是 09-12 之前的旧口径，无需再处理。

## 正确做法

处理任务遗留待办/候选清单时，先读目标笔记或文档的 frontmatter 实际状态（status 字段），不要信任任务记忆里的状态快照。任务记忆是进度日志而非权威状态源，写入后不会随笔记状态迁移自动更新。

## 根因

任务记忆（memories.md）是追加式日志，笔记状态（draft/stable/deprecated/retired）由确认闸门与合并通道独立流转，两个通道之间没有状态同步机制。

## 适用范围

任何「任务记忆里挂着待裁决/待定条目」的场景：先查实际文件状态，可能早已闭环，避免重复裁决或误立项。
