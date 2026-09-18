---
type: lesson
title: "模拟 SessionEnd 验证会触发真实采集副作用：telemetry 写入、自动 commit 与自动 push"
tags: ["lesson", "sessionend"]
metadata:
  date: 2026-09-18
  confidence_level: weak
  source_session: "7245f28d19714f71bca1abdd87568f23"
  related_modules: ["team-memory-fusion", "hooks"]
  severity: medium
  source_ref: "raw\\conv-user_command-commands-codewiki-启用-禁用任务管理（跨会话任务记忆）-管理-team-me.md"
  scene: "hook 接线验证"
status: draft
author: iamwangbao-163-com
generated: { by: codewiki/5.10.1, at: 2026-09-18T01:00:04Z }
stale_after: 2027-03-17
---

## 背景

用模拟 SessionEnd 事件（伪造 transcript_path 指向测试 JSON）验证采集 hook 时，走的是完整 capture 链路：写 `repowiki/.meta/telemetry/*.jsonl`、触发 `capture_conversation` 的自动 commit（如 `codewiki: auto-sync knowledge`），并**自动 push 到远端**——把仓库里原本未推送的其他提交（本次为 teammate 的 `5a385b8`）一并推了上去。

## 正确做法

在共享远端的仓库做模拟采集验证前，先知晓此副作用：
1. 验证前检查 `git status` / 未推送提交，评估是否可接受被顺带推送；
2. 验证后清理测试产物（删除测试 conv-*.md、复原 `repowiki/raw/.index.json`）；
3. 如需回退已推送的 auto-sync 提交，须用户显式授权（涉及 force-push），不要擅自改写 git 历史。

## 根因

capture 作为批边界自动 commit+push 是既定行为，模拟事件与真实事件走同一链路，无法只验证落盘而不触发同步。
