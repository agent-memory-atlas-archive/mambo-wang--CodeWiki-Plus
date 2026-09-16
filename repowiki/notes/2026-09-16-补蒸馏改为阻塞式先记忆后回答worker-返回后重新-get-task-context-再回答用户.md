---
type: decision
title: "补蒸馏改为阻塞式（先记忆后回答）：worker 返回后重新 get_task_context 再回答用户"
tags: ["decision"]
aliases: ["阻塞式补蒸馏", "先记忆后回答", "不阻塞已被取代", "补蒸馏时机", "pending_raw_count"]
metadata:
  date: 2026-09-16
  confidence_level: weak
  task_id: 产品维护
  related_modules: ["agents", "hooks", "mcp"]
status: draft
author: iamwangbao-163-com
generated: { by: codewiki/5.10.1, at: 2026-09-16T13:47:11Z }
stale_after: 2027-09-16
---

## 背景

2026-08-23 的设计是「委托 distill-worker 后**不阻塞**：主 Agent 立刻回话，自然停顿点再拉结果」（见 `notes/2026-08-23-会话启动时的-query-wiki蒸馏等重操作委托-subagent-执行避免阻塞用户正常使用.md`）。2026-09-16 核对现状：实现已改为**阻塞式、先记忆后回答**，但该变更一直未入库——`wiki/scenarios/任务记忆系统设计方法.md`、`wiki/modules/MCP_Prompts.md` 与任务记忆里都还写着“不阻塞”。

## 结论

`pending_raw_count > 0` 时，主 Agent 发**阻塞式**子代理补蒸馏，**等 worker 返回后重新 `get_task_context`** 拉最新记忆，再回答用户。

依据本次代码核对：

- `codewiki/agents/distill-worker.md`：description 明确「必须等本 subagent 返回后才回答用户（先记忆后回答）」；
- `tests/test_task_session_start.py:97-103`：断言 `"阻塞式" in ctx`、`"重新 get_task_context" in ctx`，注释写明 "delegated to a blocking subagent, not run inline by the main agent"。

## 理由

若边蒸馏边回答，回答用的是旧记忆，而记忆随后被改写，同一会话内就产生“答案与记忆不一致”；先蒸馏再回答牺牲首句延迟换一致性。

## 代价与边界

- 用户要为补蒸馏等待（积压多时明显）——因此 worker 侧必须有探活条款：MCP 不可见**立即停下上报**，不重试、不退让 python 直连，避免长时间空转。
- subagent 失败/超时不重试：带旧记忆直接回答，未蒸馏的 raw 留待下次会话补。
- 未变的部分：依然是委托 subagent（上下文隔离）、依然不在主 Agent 内联读 raw，授权方式用 `mcpServers` 而非 `tools:` 白名单。

