# ADR-0012: 蒸馏提取纪律吸收 hindsight 两条合并规则（reason 必带 + NO COMPUTATION）

- 状态：已接受
- 日期：2026-09-19
- 决策人：用户（grill 拷问定案）
- 关联：docs/hindsight-调研与借鉴分析.md · repowiki/notes/2026-09-19-distill聚合-prompt-吸收-hindsight-两条合并规则每条-op-必带-reason-no-compu.md · ADR-0010（通道互斥）

## 背景

hindsight（vectorize-io）consolidation prompt 有九条合并规则，调研处置从中识别出两条可吸收进本仓蒸馏提取规范：

1. **每条合并 op 必带 reason**——hindsight 侧每次 creates/updates/deletes 都必须给出可审计的理由（hindsight-api-slim/hindsight_api/engine/consolidation/prompts.py:111）；
2. **NO COMPUTATION**——"user 说卖了 X"绝不递减计数，只记录明说的数字，不做算术/逻辑推断（prompts.py:53）。

本仓现状（依据本次代码核对）：`_DISTILL_SYSTEM`（codewiki/mcp/tools/distill_conversation.py:59-121）原有 5 条提取纪律，无 reason 要求、无禁止计算条款；聚合 submit 的 dispositions 已强制 reason 字段（codewiki/mcp/prompts.py:1502），scenarios 的 action 只有 summary。

## 决策

1. **absorbed 必须有可指认的落点**（prompt 行/文档行/代码行），否则降级为 deferred——「吸收」是动作不是愿望。
2. 在 `_DISTILL_SYSTEM` 新增第 6 条纪律（两条规则合并为一条，最小落点）：

   > 6. Reasoned and literal: every note MUST state why it is worth persisting (one line in the body, e.g. under ## Rationale); and NEVER compute — record only numbers and conclusions that were explicitly stated in the conversation, never derived ones (no arithmetic, no counting, no inference over stated figures).

3. 聚合侧不动：dispositions 已强制 reason，scenarios 加 reason 属锦上添花但需动 schema，收益边际。
4. 索引抑制（hindsight #1 absorbed 项）不动代码：本仓注入现状（只列 3 条最新笔记标题 + 检索指引）已合规，靠 pitfall 笔记检索兜底。
5. deferred 2 项（page delta 刷新、4 臂 RRF 检索）不定可观测触发信号——为 deferred 建观测基建是过度工程，deferred 的本义是「明确不做的留档」，不是 backlog。

## 后果

- 正面：蒸馏产出每条笔记自带持久化理由，可审计；堵住「把明说数字做二次运算」这类确定性幻觉；一处 prompt 改动，零 schema 变更。
- 负面/代价：蒸馏 LLM 输出略增（每条 note 多一行 rationale）；「reason 必带」靠 prompt 约束而非 schema 强制，蒸馏 LLM 可能漏写——接受，因为蒸馏产物本就要过确认闸门。
- 测试：tests/test_distill_p1.py 补断言（`Reasoned and literal`、`NEVER compute`），全量 1169 passed。

## 复核

- hindsight 原文措辞「绝不递减计数，只记录明说的数字」比泛泛「不要推断」更可执行，采纳其精确措辞。
- 与既有纪律 2（准确归因）、4（AI 输出须采纳后才可提取）互补不重叠：2/4 防「把推测当结论」，6 防「把明说数字做二次运算」。
