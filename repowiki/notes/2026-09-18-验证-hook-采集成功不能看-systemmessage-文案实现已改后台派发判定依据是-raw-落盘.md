---
type: pitfall
title: "验证 hook 采集成功不能看 systemMessage 文案：实现已改后台派发，判定依据是 raw/ 落盘"
tags: ["pitfall", "sessionend"]
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
generated: { by: codewiki/5.10.1, at: 2026-09-18T00:59:52Z }
stale_after: 2027-03-17
origin: conversation

---

## 背景

按命令文档用模拟事件验证 SessionEnd 采集时，文档（含 `codewiki/mcp/prompts.py` 的 team-memory-hook prompt）写期望 stdout systemMessage 含 `"status": "captured"`，实测文案却是 `team-memory capture started in background`，一度误判为采集失败。

## 正确做法

`codewiki/hooks/capture_session_end.py` 已改为后台 detached 派发（约 214-216 行处输出 started in background 文案）。判定采集成功的正确依据是 **`repowiki/raw/` 是否落盘 conv-*.md 文件**，且需等待后台进程完成（实测 1–18 秒不等），不要依赖 systemMessage 文案。

## 根因

文档-实现漂移：实现改为后台派发后，命令文档与 prompts.py 的期望文案未同步更新。
