# 0008. 主动沉淀与蒸馏双写路径用原料标记确定性去重

日期：2026-09-17
状态：已接受

## 背景

任务记忆有两条写入路径：① 批处理路径——会话收尾采集进 `raw/`，下轮会话开始时
`distill_conversation` 蒸馏并**无条件直写**任务记忆（ADR-0002）；② 主动沉淀
（active settle）——Agent 在自然停顿点直写 `add_task_memory`，为 trae 企业版
（无 SessionEnd、Stop 不带 transcript）等采集链路断供的宿主提供"下轮无延迟"的
记忆通道，hook 宿主亦可显式开启形成"prompt 写 + hook 读"共存。

两条路径同时生效时必然双写：Agent 停顿点写了"已把 X 改为 Y"，收尾轮又把整个
会话采集进 raw，蒸馏从原文里把同一条进度再提炼一遍。而 `append_task_memories_direct`
是纯追加、**无任何去重**（笔记有标题 Jaccard 等，任务记忆没有），双写即噪声，
且 40 条/24KB 的压缩阈值被无谓消耗。

## 决策

采用**原料标记 + 确定性规则**：`capture_conversation` 落盘的 `conv-*.md` frontmatter
新增顶层单行键 `active_settle: true`（由沉淀协议在采集时声明"本会话记忆已直写"）；
`distill_conversation` 见到该标记即**只产出草稿笔记、跳过任务记忆生成**。规则写在
工具层，不依赖任何提示词或 LLM 自觉。无标记的存量行为逐字节不变。

## 理由

1. **候选方案的真实取舍**。提示约束（蒸馏 prepare 的 system_prompt 声明"已主动
   沉淀则只出笔记"）把正确性押在 LLM 自觉上，链路长易漂移；不防重靠压缩兜底则
   在双写发生后才收敛，期间 `get_task_context` 注入双倍条目。原料标记是唯一把
   去重做成不变量的方案。
2. **语义自洽**。标记表达的事实（"记忆已由更及时的通道落盘"）与跳过动作（"蒸馏
   不再补记忆"）一一对应；蒸馏仍产笔记，保证漏网的通用经验有兜底原料——这正是
   保险采集保留的唯一职责。
3. **符合闸门分轨**。跳过的是任务记忆（本无闸门，ADR-0002），笔记的 draft→confirm
   两区制（ADR-0004）不受影响。

## 已知限制

- 标记是 Agent 自报的软事实：协议没遵守（该沉淀没沉淀）而采集时误带标记，该会话
  的记忆就漏了——靠下轮 `get_task_context` 的 `pending_raw_count` 与人工复盘兜底，
  与所有 prompt 驱动约束同级别的风险，接受。
- 混合会话（沉淀一半、剩下一半靠蒸馏）被标记整体跳过记忆生成，粒度为会话级不做
  条目级对账。条目级对账需要记忆去重能力，成本不成比例。

## 后果

- `capture_conversation` 接受并透传 `active_settle` 参数进 frontmatter（顶层单行键，
  遵守 stdlib-only hook 的逐行扫描约束，见 CONTEXT.md "frontmatter module"）。
- `distill_conversation` 的记忆直写步骤由无条件改为条件执行；跳过时响应以字段显式
  声明（而非静默少做事）。
- `task_session_start.py` 无需改动：它只按 `pending` 计数触发补蒸馏，标记的存在
  不改变"该蒸馏"本身（笔记仍要蒸馏）。
