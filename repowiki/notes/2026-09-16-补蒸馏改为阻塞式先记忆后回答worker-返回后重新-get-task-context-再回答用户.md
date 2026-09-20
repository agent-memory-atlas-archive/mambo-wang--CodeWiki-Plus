---
type: decision
title: 补蒸馏改为阻塞式（先记忆后回答）：worker 返回后重新 get_task_context 再回答用户
tags:
- decision
aliases:
- 阻塞式补蒸馏
- 先记忆后回答
- 不阻塞已被取代
- 补蒸馏时机
- pending_raw_count
metadata:
  date: 2026-09-16
  confidence_level: shadow
  task_id: 产品维护
  related_modules:
  - agents
  - hooks
  - mcp
status: deprecated
author: iamwangbao-163-com
generated:
  by: codewiki/5.10.1
  at: 2026-09-18 01:05:39+00:00
stale_after: '2027-09-18'
source_conversations:
- conversations/conv-working_memory_content-The-following-is-the-existing-working-2.md
verified:
- by: human:wangbao
  at: '2026-09-18T01:49:04Z'
reject_reason: consolidated into 任务记忆系统设计方法（演进：阻塞式已被推翻，改回异步）
---

## 背景

补蒸馏 subagent 原为阻塞式（等 subagent 返回后才回答用户），实际执行中 Agent 倾向先回答用户，阻塞式文案形同虚设。用户要求改回异步。

> 本笔记**推翻**了 2026-09-16 的「补蒸馏改为阻塞式（先记忆后回答）」决策——阻塞式与「用户在等回答」存在指令冲突，实际遵循率低，改回异步。

## 根因分析

AGENTS.md 协议块不稳定触发的根因**不是内容量问题**（200 行/15.7KB 不算大），而是：
1. 「阻塞等待 subagent」与「用户在等回答」直接指令冲突，Agent 倾向先回答；
2. AGENTS.md 是文档层软约束，遵循率天然低于 hook 的 `additionalContext` 硬通道；
3. 协议块嵌在长文档中部，注意力权重被稀释。

精简文档或拆独立 rule 收益有限——rule 机制同样是 prompt 层软约束，换位置不解决指令冲突。

## Decision

**异步化消除冲突本身**：主 Agent 发完蒸馏 subagent 直接回答用户，不等返回；自然停顿点（里程碑/话题切换/收尾轮）重新 `get_task_context` 拉取蒸馏结果、展示待确认草稿。取舍：接受「旧记忆先答、新记忆下轮可见」。

回退成本低：`ecc4fcf`（8-16）之前就是异步形态，阻塞式只是文案层改动（hook 注入文案 + prompts.py 协议块 + distill-worker 描述 + 测试断言），无逻辑代码。

同步更新点：`codewiki/hooks/task_session_start.py` 三处、`codewiki/mcp/prompts.py`（AGENTS.md 协议块 + task-workflow prompt）、`codewiki/agents/distill-worker.md` 与 `.claude.md`、已装副本（`.codebuddy`/`.qoder`/`.trae`）、`tests/test_task_session_start.py` 断言。
