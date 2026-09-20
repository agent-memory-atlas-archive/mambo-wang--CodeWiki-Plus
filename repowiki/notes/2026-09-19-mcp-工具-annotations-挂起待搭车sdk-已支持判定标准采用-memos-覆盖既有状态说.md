---
type: decision
title: MCP 工具 annotations 挂起待搭车：SDK 已支持、判定标准采用 memos 覆盖既有状态说
tags:
- decision
metadata:
  date: 2026-09-19
  confidence_level: weak
  related_modules:
  - mcp
status: stable
author: iamwangbao-163-com
generated:
  by: codewiki/5.10.1
  at: 2026-09-19 11:05:10+00:00
stale_after: '2027-09-20'
verified:
- by: human:wangbao
  at: '2026-09-20T02:38:19Z'
---

## 背景

memos 调研（docs/memos-调研与借鉴分析.md）提出借鉴其 MCP 工具 annotations 机制（readOnlyHint/destructiveHint，catalog.go:371-401）。Grill 轮裁决：值得借鉴但**挂起，不单独立项**。

## 决策

1. **挂起搭车**：registry `_register` 加可选 `annotations` 参数的改动方向确定（SDK 层 `mcp/types.py:1329` 已支持 `Tool.annotations`），但不为它单独开契约变更，等下次 registry 契约变更时顺路落地。
2. **判定标准采用 memos 说**：覆盖/删除既有状态 → destructive；纯新建 → 非 destructive。宁严勿松会让警告泛滥失去信号价值，宁窄漏掉 edit_doc_file 这类可逆但破坏性的操作。
3. **术语不进 CONTEXT.md**：MCP 协议术语是外部协议事实，不是本仓领域词汇，进词汇表只会稀释。

## 根因

- Team Doctrine「成本可见性优先于新造能力」+「搭收敛点」：单独 PR 的成本大于收益，宿主侧消费行为未证实，收益目前只是「未来兼容」。
- annotations 是客户端提示不是安全机制（mcp/types.py:1251-1256 明确 hint 不保证忠实描述），所以判定标准选「信号价值最大化」而非「安全边界最大化」。

## 适用范围

下次 registry 契约变更（如 structuredContent/错误形状落地时）一并实现；实现时 destructive 集合 = {_PUSH_ON_WRITE 中覆盖类} ∪ {delete_task, edit_doc_file, reject_note}，其余写类工具（confirm_note/ingest_note/batch_set_status）按 memos 标准不标 destructive。
