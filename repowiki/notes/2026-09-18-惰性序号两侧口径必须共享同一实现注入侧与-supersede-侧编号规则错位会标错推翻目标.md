---
type: pitfall
title: "惰性序号两侧口径必须共享同一实现：注入侧与 supersede 侧编号规则错位会标错推翻目标"
tags: ["e02", "pitfall"]
metadata:
  date: 2026-09-18
  confidence_level: weak
  source_session: "44b4bea9c40947d09554371636e88cac"
  related_modules: ["team-memory-fusion", "mcp"]
  severity: medium
  source_ref: "raw\\conv-user_command-commands-codewiki-启用-禁用任务管理（跨会话任务记忆）-管理-team-me-3.md"
  scene: "任务记忆治理实施"
status: draft
author: iamwangbao-163-com
generated: { by: codewiki/5.10.1, at: 2026-09-18T01:11:17Z }
stale_after: 2027-03-17
---

## 背景

code-review 发现 ADR-0009 实现的 D2 严重错位：注入侧 `_entry_display_ids` 只对**无持久 ID** 的条目编号且跨 own+legacy 文件合并编号；而 `supersede_memory`（store.py）对 own 文件**全部 dated 条目**递增编号。同一 `#e02` ref 在两侧指向不同条目——own 文件存在持久 ID 条目时，supersede 可能**标错推翻目标**（把退役标记打到错误条目上）。

## 正确做法

1. 「排序 + 编号」这类两侧共用的规则只留一份实现（单点收敛），注入侧与写入侧都调它，禁止两处各写一套；
2. code-review 的正确性问题（标错目标 > 功能缺失 > 文档瑕疵）应最优先修复；
3. 同轮评审还发现：坏 ref 时新条目已落盘、返回 `ok:true`+`supersede_error`（规格要求返回 error 且不留无主条目）；检索侧 `search_memories` 未按验收链 1/D7 过滤 superseded 条目——评审后须对照验收链逐项核对，而非只看测试绿。

## 教训

测试全绿 ≠ 符合规格：验收链条目要逐条映射到测试，两侧口径类逻辑要靠共享实现而非约定对齐。
