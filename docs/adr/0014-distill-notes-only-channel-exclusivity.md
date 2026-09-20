# 0014. 蒸馏固定只产经验笔记：任务记忆通道归主动沉淀独占

日期：2026-09-20
状态：已接受
取代：[ADR-0008](0008-active-settle-deterministic-dedup.md)

## 背景

ADR-0008 用「原料标记 + 确定性规则」解决主动沉淀与蒸馏的双写问题：采集时声明
`active_settle: true`，蒸馏见标记跳过任务记忆生成。该方案的前提是**两条记忆通道
并存**——批处理蒸馏仍是任务记忆的合法来源，标记负责区分"已直写"与"未直写"。

2026-09-20 的产品决策改变了这个前提：主动沉淀升为**唯一**记忆写入通道（固定启用，
不再有 per-agent 开关），采集→蒸馏链路降级为可关的备胎（`install-hooks --capture
on|off`）。一旦主动沉淀成为唯一通道，标记的存在意义随之消失：

1. **补蒸馏路径（task_id 过滤的 catch-up）本就默认 `skip_memories=true` 只产笔记**
   （ADR-0010 通道互斥），标记在该路径是冗余的。
2. 标记真正起作用的只剩非补蒸馏路径（手动批量蒸馏、Mode B 后台蒸馏），而这些路径
   的存量 raw 大多采集于「主动沉淀固定开」之前——标记缺失不代表记忆已直写，标记
   存在也不代表覆盖完整（会话级粒度，ADR-0008 已知限制）。
3. 维护标记机制的成本（参数、frontmatter 键、解析分支、测试）在单通道模型下没有
   对应收益。

## 决策

1. **蒸馏无条件只产经验笔记，不产任务记忆**——所有路径（Mode A/B/C、补蒸馏、手动
   批量）统一为 notes-only；跳过以 `memories_skipped_reason: "channel_exclusive"`
   显式声明，不静默。
2. **删除 `capture_conversation` 的 `active_settle` 参数与 frontmatter 顶层键**；
   存量 raw 中的历史标记成为无害残留（解析端不再读取）。
3. **主动沉淀固定启用**：`install-hooks` 不再有 `--active-settle` 参数（传入即硬
   报错），CODEWIKI-ACTIVE-SETTLE 协议块恒渲染；块 ②「收尾轮保险采集」整节删除，
   收尾轮兜底改为判据 4 的沉淀自查（漏沉淀补写，而非采集全文）。
4. **采集注册独立开关**：`--capture on|off`（默认 on）只控制 SessionEnd（trae 为
   Stop）采集注册的写入与移除；SessionStart（任务关联）、UserPromptSubmit（技能
   提示）与 hook 脚本、distill-worker 拷贝不受影响。

## 理由

1. **单通道模型下标记是僵尸机制**。ADR-0008 的核心价值是"区分两条通道谁写了记忆"；
   只剩一条通道后无物可区分。保留参数只会让调用方误以为还有第二通道。
2. **确定性优先于押自觉**（继承 ADR-0008 的立场）：与其靠标记声明"已直写"（软事实，
   会漏报），不如把"蒸馏不产记忆"做成无条件不变量——规则更简单，且不可能因标记
   缺失而误产双写。
3. **代价已知情接受**：存量积压 raw 的记忆内容不再落任务记忆（只产笔记）；Agent
   漏沉淀的会话失去蒸馏捞回兜底。漏报率由观察期数据（设计方案 §7.3）验证，若
   主动沉淀遵守度不达标，可重开 capture 恢复采集链路。

## 已知限制

- 蒸馏产出的笔记仍走 draft→confirm 闸门（ADR-0004），本 ADR 不改变笔记生命周期。
- `skip_memories` 参数（ADR-0010）保留现状：它管的是补蒸馏路径的显式开关语义，
  与本 ADR 的无条件 notes-only 在响应字段上兼容（`channel_exclusive` 优先呈现）。

## 后果

- `capture_conversation` / `store.capture_raw` 删除 `active_settle` 参数；
  `distill_conversation` 删除标记解析分支与 `_parse_llm_memories` 调用，
  `memories_written` 恒为 0。
- `install_hooks` / `install_for_ide` / `merge_settings_json` 增加 `capture` 参数；
  `hooks.yaml` 删除 `active_settle` 字段，`active_settle_of()` 退役。
- `--status` 表 `active_settle` 列删除，新增 `capture` 列；wired-on-disk 新增
  `hooks(仅SS)+settings(capture off)` 专用值，与「接线不完整」区分。
- MCP prompt `team-memory-hook` / `init-wiki` 参数 `active_settle` → `capture`，
  locales zh/en 同步。
- 测试：`test_active_settle_dedup.py` 随机制删除；接线矩阵、CLI、prompt、registry
  测试按新语义改写。
