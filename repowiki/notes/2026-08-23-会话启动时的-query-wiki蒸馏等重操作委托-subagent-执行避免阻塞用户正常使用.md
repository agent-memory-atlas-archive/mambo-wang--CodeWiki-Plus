---
type: decision
title: 会话启动时的 query_wiki/蒸馏等重操作委托 subagent 执行，避免阻塞用户正常使用
tags:
- decision
- readfile
metadata:
  date: '2026-08-23'
  task_id: 产品维护
  related_modules:
  - task_manager
  - wiki/scenarios/任务记忆系统设计方法.md
  severity: medium
  source_ref: conversations/conv-开始新对话触发选择任务后，会有query_wiki以及蒸馏操作，这些操作可以放到subagent执行吗，别影响用户正常使.md
  scene: 任务记忆/补蒸馏
  consolidated_into:
  - ''
  - wiki/scenarios/任务记忆系统设计方法.md
  confidence_level: shadow
status: deprecated
generated:
  by: codewiki/5.3.0
  at: '2026-08-23 08:00:48+00:00'
stale_after: '2027-08-26'
origin: conversation
verified:
- by: human:wangbao
  at: '2026-08-25T16:48:21Z'
author: mambo-wang
reject_reason: consolidated into 任务记忆系统设计方法
---

## Background

用户提出：开始新对话触发选择任务后，会有 query_wiki 以及蒸馏操作，这些操作如果由主 Agent 亲自执行会阻塞用户正常使用——主 Agent 埋头逐条 read_file 读 raw 原文、提取知识，用户提问被明显拖慢，且大量对话原文灌入主会话上下文。

## Decision

将补蒸馏等重操作委托 subagent 执行：创建 `.codebuddy/agents/distill-worker.md`（project 级、agentic 模式，授权 codewiki MCP），主 Agent 在检测到 pending_raw_count > 0 时用 Task 工具 spawn 它执行 Mode C 蒸馏（prepare → 逐条 read_file 提取 → submit）；在自然停顿点拉取结果并向用户展示待确认项。

> **2026-09-16 更新（本条的下述两处细节已被取代）**：① 授权方式改为 `mcpServers: [codewiki]`——原写法 `tools: ReadFile` 是白名单会把 MCP 工具一起挡掉，`toolsMCP` 又是非官方字段无效，两者叠加导致 worker「0 tool uses 空转」；② 执行方式由「后台不阻塞」改为**阻塞式、先记忆后回答**——主 Agent 必须等 worker 返回并重新 `get_task_context` 后才回答用户。「委托 subagent 执行」这一主结论仍然有效。参见 `notes/2026-09-16-补蒸馏改为阻塞式先记忆后回答worker-返回后重新-get-task-context-再回答用户.md`、`notes/2026-09-16-修-subagenthook-定义只改已装副本会被-install-hooks-覆盖打回必须改随包源变体并加源变体守门测.md`。

## Rationale

- 上下文隔离：raw 原文在 subagent 独立上下文消化，主会话只留摘要级信息。
- ~~不阻塞：spawn 后主 Agent 立即返回用户问题，蒸馏后台完成。~~ **已被取代（2026-09-16）**：改为阻塞式、先记忆后回答——先蒸馏落记忆、再回答用户，避免"回答时记忆还是旧的"。
- 权限边界 + 评审闸门分离：subagent 授权 codewiki MCP（`mcpServers`），且不执行 confirm_note/reject_note——笔记草稿的正式落盘必须由主 Agent 与用户确认（任务记忆由 `distill_conversation` 直写落盘，无需确认——ADR-0002）。

## 相关文档

- [任务记忆系统设计方法](../wiki/scenarios/任务记忆系统设计方法.md)
- [对话蒸馏管线与 raw 暂存区](../wiki/scenarios/对话蒸馏管线与raw暂存区.md)
