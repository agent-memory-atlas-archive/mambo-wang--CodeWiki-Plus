---
type: decision
title: 决策：任务记忆从 append-only 放宽为 append + 受控降状态（ADR-0009）
tags:
- a3f2
- decision
- e01
- sequencematcher
- 新id
metadata:
  date: 2026-09-18
  confidence_level: weak
  source_session: 44b4bea9c40947d09554371636e88cac
  related_modules:
  - team-memory-fusion
  - mcp
  severity: high
  source_ref: conversations/conv-user_command-commands-codewiki-启用-禁用任务管理（跨会话任务记忆）-管理-team-me-3.md
  scene: 任务记忆治理
status: stable
author: iamwangbao-163-com
generated:
  by: codewiki/5.10.1
  at: 2026-09-18 01:10:55+00:00
stale_after: '2027-09-18'
origin: conversation
verified:
- by: human:wangbao
  at: '2026-09-18T01:47:04Z'
---

## 背景

调研 12 篇记忆项目文档后定位薄弱面在任务记忆通道：直写追加、无去重、无质量门、无失效语义。经 11 轮 grill 定案。

## Decision（D1-D11 摘要）

- **supersede**：新条目带持久短 ID（`### 时间戳 #a3f2`，4 位 base36 防撞）；存量条目注入时惰性补号（`#e01`…，不回写文件）；推翻 = 被引用条目头下插单行 `> [superseded 日期 by #新ID]` 标记，走 `locked_rmw` 原子改写；注入/检索跳过退役条目，压缩优先摘出。
- **写入检查**：difflib `SequenceMatcher` ratio > 0.85 拒绝并返回最相似条目（唯一硬拒点）；比对剥离条目头、短文本（<20 字符）豁免；压缩窗口软上限超限警告放行；supersede 写入跳过去重。
- **压缩分级**：`compaction_due` 布尔升级为 green/yellow/orange/red 四档（按既有 40 条/24KB 阈值 75%/87.5%/100% 内插，双维取 max）；压缩维持**读取驱动**（`get_task_context` 携带 `compaction_work`），写侧只报 `hot_entries` 计数不干活。
- **存储格式维持 Markdown**（ADR-0001 不动），所有改动是 markdown 内联约定。横向对比确认：随业务仓 git 版本化 + Markdown 存记忆全场只有 teamai-cli 与本仓，是自洽选择。
- **明确不做**：mem0 无闸门自动 UPDATE/DELETE、半衰期衰减、自动冲突发现、向量检索、蒸馏事件流。

## 落点

ADR：`docs/adr/0009-task-memory-supersede-and-write-check.md`；设计文档：`docs/任务记忆退役与写入检查设计方案.md`（D1-D11 + 9 条验收链 + 四批次切分）；术语落 `CONTEXT.md`（退役 retired / 写入检查 write check）。
