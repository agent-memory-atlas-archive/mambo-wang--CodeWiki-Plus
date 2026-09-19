---
type: decision
title: "memos 调研处置：1 absorbed 挂起搭车 / 3 deferred / 6 excluded，当前无立即落地项"
tags: ["1", "6139", "9", "decision", "toolannotations"]
metadata:
  date: 2026-09-19
  confidence_level: weak
  task_id: 他山之石
  source_session: "d30d6164edba4f13ada8ca7a51b8ac13"
  related_modules: ["mcp"]
  severity: medium
  source_ref: "raw\\conv-working_memory_content-The-following-is-the-existing-working.md"
  scene: "他山之石竞品调研"
status: draft
author: iamwangbao-163-com
generated: { by: codewiki/5.10.1, at: 2026-09-19T11:28:52Z }
stale_after: 2027-09-19
---

## 背景

2026-09-19 对 usememos/memos（自托管短笔记应用，Go + React，40k+ star，基线 v0.31.0-rc.2-16-g7e3d3c6）做源码调研，报告存档 `docs/memos-调研与借鉴分析.md`。业务上与本仓无重叠，但其 `server/mcp/` 是迄今调研项目里 MCP 协议合规工程最完善的样本——每个机制都对应真实 issue，非 speculative 设计。

## 裁决

10 个候选处置为 1 absorbed（挂起）/ 3 deferred / 6 excluded，**当前无需要立即落地的项**：
- **absorbed 但挂起搭车**：工具 annotations（`catalog.go:371-401` 从 HTTP 方法推导 readOnly/destructive/idempotent hint + 覆盖表修正）——SDK 层已支持（`mcp/types.py:1329` `Tool.annotations: ToolAnnotations | None`），改动方案已定（registry `_register` 加可选参数），但等下次 registry 契约变更时顺路落地，不单独立项。判定标准采用 memos「覆盖/删除既有状态 → destructive」：destructive 集合 = {`edit_doc_file`, `reject_note`, `delete_task`}；`confirm_note`/`ingest_note`/`batch_set_status` 不标（宁严勿松会让警告泛滥失去信号价值）。详见笔记『MCP 工具 annotations 挂起待搭车』。
- **deferred**：structuredContent/outputSchema + 错误形状（等 strict 宿主出现；错误结果刻意不带 structuredContent，避免 strict 客户端拿错误载荷对成功 outputSchema 校验，修 #6139）；任务级 eval（15 个 QA 钉在确定性种子数据上，测 LLM 组合工具能否答对真实问题——并入质量量化主线，与 llm-wiki-compiler 调研 #1/#9 合流）。
- **excluded**：OpenAPI 驱动（本仓无 REST 层）、CEL→SQL（无 SQL 存储）、goldmark AST（markdown 是存储非渲染）、目录 TTL（stdio 无 discover 流）等 6 条。

## 价值定位

memos 的价值在于把「值得借鉴」的判定标准校准得更准：36 个工具的 MCP server，真正能搬的只有协议层三个小机制，且每一个都因「触发条件未到」而不该现在动手——改动方向确定 ≠ 现在做（成本可见性优先于新造能力）。唯一可执行后续动作：下次有人动 `registry.py` 契约时把 annotations 一起带上。

## 适用范围

后续重启 deferred 项（strict 宿主出现、质量量化主线立项）时以本处置为基线；对同类 MCP server 工程做调研时可直接引用。与『llm-wiki-compiler 调研处置』『cognee 调研处置』同层互补（具体项目处置结论层），与『MCP 工具 annotations 挂起待搭车』（单项机制决策层）互补不重复。
