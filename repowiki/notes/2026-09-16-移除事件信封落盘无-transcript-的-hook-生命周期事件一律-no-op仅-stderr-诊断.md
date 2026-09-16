---
type: decision
title: "移除事件信封落盘：无 transcript 的 hook 生命周期事件一律 no-op（仅 stderr 诊断）"
tags: ["decision", "precompact", "sessionend"]
aliases: ["事件信封", "envelope 落盘", "SessionEnd 无 transcript", "hook 采集降级 no-op"]
metadata:
  date: 2026-09-16
  confidence_level: weak
  related_modules: ["hooks", "mcp", "capture"]
status: draft
author: iamwangbao-163-com
generated: { by: codewiki/5.10.1, at: 2026-09-16T13:08:20Z }
stale_after: 2027-09-16
---

## 背景

`_ide_hook.py` 处理 SessionEnd/Stop/PreCompact 事件时，若既无内联 turns 又无可读 `transcript_path`，曾把事件本身合成为一条 1 行伪对话（"事件信封"，`role=user`）落进 `repowiki/raw/`，用途是"确认 hook 确实触发过 + 留下 IDE 注入的 payload 形状"。

## 结论

该落盘路径已整体移除：信封分支只向 stderr 打印诊断后 `return 0`，磁盘零写入（依据本次代码核对：`codewiki/mcp/_ide_hook.py:496-520`）。同时删除两处专为信封存在的补丁——`is_envelope` 标记，以及"信封必须置空 `source_session_id` / `task_id`"的特判；现在能走到 capture 的一定是真实会话，可放心携带 session 归属与 task 绑定。

## 根因

信封从"留痕"变成负债，是四个理由叠加：

1. **零知识密度**：没有 user/assistant 正文，蒸馏只能提交空结果，纯占 raw 积压位；
2. **无归属**：不带真实 task_id/session，进不了任何任务记忆；
3. **有数据丢失风险**：`capture_conversation` 按 `source_session_id` supersede 去重，信封若带同 session id，会用一行诊断文本覆盖刚采到的完整 transcript——此前靠"信封置空 session id"特判规避，属于用特例给一个不该存在的分支兜底；
4. **诊断使命已完成**：TRAE Stop 与 cursor stop 的载荷形状都已探明（确认不带 transcript），不需要继续落样本取证。

## 适用范围

所有"事件触发但无数据来源"的 hook 采集兜底：默认 no-op + stderr 诊断，不落占位记录。payload 形状诊断改由 wrapper 的 `.hook-debug/event-<ts>.json` 承担。要真正覆盖漏采，只能等宿主给 transcript，或由 Agent 按 AGENTS.md「会话收尾轮」norm 中介采集补漏。

## 取代关系

取代 `notes/2026-09-08-sessionend-hook-触发但-ide-未提供-transcript-时只落一条事件信封进-raw-积压.md`——它把"raw 里出现空信封"记为预期行为并指引"蒸馏时直接跳过"，结论方向已反转。`notes/2026-08-09-hook-事件信封合成时须置空-source-session-id否则-supersede-会覆盖真实-transcri.md` 的具体做法（is_envelope 特判）一并作废，但其通用教训仍成立：**任何合成的非真实记录都不得复用真实捕获的 session 标识**。
