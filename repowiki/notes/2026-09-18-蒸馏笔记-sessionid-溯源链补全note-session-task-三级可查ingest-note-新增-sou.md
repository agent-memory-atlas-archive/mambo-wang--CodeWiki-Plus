---
type: architecture
title: "蒸馏笔记 sessionId 溯源链补全：note → session → task 三级可查（ingest_note 新增 source_session 参数）"
tags: ["architecture"]
metadata:
  date: 2026-09-18
  confidence_level: weak
  task_id: OpenWiki-竞品调研
  source_session: "0c273f6722ee4063b6e47fdae1ff47e3"
  related_modules: ["team-memory-fusion", "mcp"]
  severity: medium
  source_ref: "conversations/conv-working_memory_content-The-following-is-the-existing-working-2.md"
  scene: "任务记忆 / 溯源链"
status: draft
author: iamwangbao-163-com
generated: { by: codewiki/5.10.1, at: 2026-09-18T01:04:29Z }
stale_after: 2027-09-18
origin: conversation

---

## 背景

用户希望蒸馏产物能同时关联任务与 sessionId。核对发现：`capture_conversation` 已接受 `source_session_id` 写入 raw frontmatter，`set_session_task` 把绑定落 `repowiki/.meta/task_bindings/<source_session_id>.json`，蒸馏笔记经 `task_id` 路由到任务——缺的只是蒸馏笔记 frontmatter 也带 session 溯源。

## 实现要点

- `note_ingest.py`：`ingest_note` 新增 `source_session` 参数，写入笔记 metadata（与 `task_id` 并列）；
- `distill_conversation.py`：submit 时从 raw frontmatter 读 `source_session` 传给笔记；
- 溯源链：note → session → task 三级可查；
- 守门测试 `test_distill_note_carries_source_session`（注意 submit 响应结构是 `distilled[0]["notes"][0]["note_file"]`）。

## 验证

全量测试 1147→1148 通过。
