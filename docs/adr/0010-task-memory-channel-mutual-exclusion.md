# 0010. 任务记忆通道互斥：补蒸馏路径固定只产经验笔记

日期：2026-09-18（补记——决策先于本 ADR 落地，代码引用曾悬空指向 ADR-0009）
状态：已接受

## 背景

任务记忆有两条写入路径：主动沉淀（active settle，`add_task_memory` 停顿点直写，
ADR-0002/0008）与蒸馏直写（`distill_conversation` 的 `append_task_memories_direct`）。
ADR-0008 用 `active_settle: true` 原料标记做了会话级去重——标记声明「本会话记忆
已直写」，蒸馏见标记即跳过记忆生成。

但标记是 Agent 自报的软事实：协议没遵守（该沉淀没沉淀）而采集时误带标记，该会话
的记忆就漏了；反之，主动沉淀协议全面铺开后（CODEWIKI-ACTIVE-SETTLE），会话收尾
的保险采集几乎总是带着已直写的记忆进 raw，蒸馏再产记忆就是确定性双写。

## 决策

**通道互斥**：`distill_conversation` 的 task_id 过滤路径（sessionStart 补蒸馏
catch-up，覆盖 prepare/submit/batch/Mode B）**固定** `skip_memories=true`——
只产经验笔记，任务记忆归主动沉淀通道直写。无 opt-out 开关（固定语义，不把
正确性押在调用方传参上）。

- 跳过以响应字段显式声明（`skip_memories: true` + `memories_note`），不静默
  少做事；提取方产出的 memories 被确定性丢弃（`memories_skipped_reason=
  skip_memories`）。
- 非任务过滤路径（全局批处理蒸馏）不受本 ADR 约束，仍走 ADR-0008 的原料标记
  条件跳过。

## 理由

1. **把去重从软事实升级为不变量**。ADR-0008 的标记依赖 Agent 自觉；通道互斥
   把「补蒸馏不写记忆」写死在工具层，双写在这条路径上不可能发生。
2. **职责清晰**。主动沉淀是任务记忆的默认通道（及时、停顿点即写）；补蒸馏的
   唯一职责是捞回漏沉淀的通用经验（笔记），再写记忆只会与直写通道竞争。
3. **与 ADR-0009 写入检查互补**。通道互斥防跨通道双写，写入检查（difflib 去重）
   防同通道近重复——两层防线各管一段。

## 已知限制

- 补蒸馏期间主动沉淀没发生的会话（Agent 全程未命中停顿点），其任务进度只能靠
  下轮会话的 `get_task_context` 现场重建——接受，进度类信息时效性强，隔轮补记
  价值有限。
- 全局批处理路径仍依赖 ADR-0008 标记，软事实风险在那条路径上保留。

## 后果

- `distill_conversation` task_id 过滤分支固定 skip_memories；响应携带
  `skip_memories`/`memories_note`/`memories_skipped_reason` 字段。
- `task_session_start.py` hook、distill-worker subagent 提示、AGENTS.md 协议块
  的「通道互斥」引用统一指向本 ADR。
