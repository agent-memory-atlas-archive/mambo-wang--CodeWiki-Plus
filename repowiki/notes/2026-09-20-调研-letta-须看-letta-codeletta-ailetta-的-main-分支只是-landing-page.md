---
type: pitfall
title: "调研 letta 须看 letta-code：letta-ai/letta 的 main 分支只是 landing page"
tags: ["pitfall", "typescript"]
metadata:
  date: 2026-09-20
  confidence_level: weak
  task_id: 他山之石
  source_session: "8963b3e1a98b4608a6ab4e05850d2702"
  severity: medium
  source_ref: "conversations/conv-working_memory_content-The-following-is-the-existing-working-3-50176a.md"
  scene: "竞品调研（他山之石）"
status: draft
author: iamwangbao-163-com
generated: { by: codewiki/5.10.1, at: 2026-09-20T03:22:08Z }
stale_after: 2027-03-19
origin: conversation

---

## 背景

2026-09-19 调研 Letta（https://github.com/letta-ai/letta）时，克隆 main 分支后发现仓库根目录只有 landing page 代码；其 AGENTS.md 明确说明当前实现已迁移至 letta-ai/letta-code（TypeScript 编码 agent）。若只读 letta 仓会得出完全过时的结论（例如误以为核心仍是 Python 服务 + 向量记忆库）。

## 正确做法

克隆竞品仓后，先读 README.md 与 AGENTS.md 确认该仓是否为真正的实现仓；发现「实现已迁移 / moved to ...」指向时，立即克隆指向的新仓再读代码。letta 的正确调研对象是 letta-ai/letta-code（src/agent/ 下的 memory-filesystem.ts、reflection-runs.ts、prompts/letta.md 等）。

## 根因

Letta 项目从 Python 记忆服务转型为 TypeScript 编码 agent，旧仓保留作门面（landing page），GitHub 仓库名与实际实现脱钩。

## 适用范围

所有竞品调研（他山之石任务模式）；仓库名 ≠ 实现仓是常见情况（组织转型、monorepo 拆分均会出现）。
