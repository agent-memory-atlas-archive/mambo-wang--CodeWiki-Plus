---
type: architecture
title: AGENTS.md 三个 codewiki 管理块的权威源与再生成入口
tags:
- architecture
- codewiki
metadata:
  date: 2026-09-18
  confidence_level: weak
  task_id: 产品维护
  source_session: 21b7dedf054c44bfbec90d72f16ba0b4
  related_modules:
  - agents-md
  - prompts
  - locales
  severity: medium
  source_ref: conversations/conv-working_memory_content-The-following-is-the-existing-working-2-e83954.md
  scene: 产品维护-AGENTS.md 精简
status: stable
author: iamwangbao-163-com
generated:
  by: codewiki/5.10.1
  at: 2026-09-18 06:16:35+00:00
stale_after: '2027-09-18'
origin: conversation
verified:
- by: human:wangbao
  at: '2026-09-18T06:42:11Z'
---

## 背景

用户要求精简 AGENTS.md（约 200 行太长）。codewiki 通过标记块管理其中三个块，各有独立权威源，直接手改 AGENTS.md 会被 install-hooks 覆盖打回。

## 结构事实

| 块 | 权威源 | 再生成入口 |
|---|---|---|
| CodeWiki LLM Wiki（~122 行） | `codewiki/mcp/locales/zh.yaml` / `en.yaml` 的 `artifacts.agents_md.main` | `codewiki.mcp.tools.agents_md.write_agents_md` |
| TEAM-MEMORY-TASK（~21 行） | `codewiki/mcp/prompts.py` 的 `_TASK_MEMORY_AGENTS_SECTION` | `codewiki.cli.utils.ide_config.upsert_task_memory_section` |
| CODEWIKI-ACTIVE-SETTLE（~20 行） | `codewiki/mcp/prompts.py` 的 `_active_settle_section()` | `codewiki.cli.utils.ide_config.upsert_agents_section` |

「Agent skills」和「Team memory fusion」两段是手写内容，不在标记块管理范围，精简需手工编辑。

## 精简约束

改这些块前先 `search_content` tests/ 查断言短语——守门测试硬编码了大量短语（使用建议、采纳声明、标注依据、纠正识别、四问过滤、路由表、归档示例、OrderService 示例、语言闸门），精简措辞时必须保留，否则测试挂。2026-09-18 实测：保留全部断言短语的前提下压缩冗余表述，AGENTS.md 约 200 行 → 165 行，122+109 测试全绿。
