---
type: decision
title: 主动沉淀协议三缺口修复：判据扩面、每轮收尾自查、双通道独立声明（ACTIVE-SETTLE 块）
tags:
- codebuddy
- decision
- sessionstart
metadata:
  date: 2026-09-18
  confidence_level: weak
  task_id: 产品维护
  source_session: 21b7dedf054c44bfbec90d72f16ba0b4
  related_modules:
  - prompts
  - agents-md
  severity: medium
  source_ref: conversations/conv-working_memory_content-The-following-is-the-existing-working-2-e83954.md
  scene: 产品维护-主动沉淀协议
status: stable
author: iamwangbao-163-com
generated:
  by: codewiki/5.10.1
  at: 2026-09-18 06:16:02+00:00
stale_after: '2027-09-18'
origin: conversation
verified:
- by: human:wangbao
  at: '2026-09-18T06:41:31Z'
---

## 背景

用户反馈「感觉没有触发自动记忆」：会话中只写了 IDE 工作记忆（`.codebuddy/memory/`），任务记忆通道（`add_task_memory`）一直空着。实证诊断出主动沉淀协议（AGENTS.md 的 CODEWIKI-ACTIVE-SETTLE 块）存在三个真实缺口，本次会话全部踩中。

## 三个缺口

1. **四判据覆盖面不够**：纯 Q&A 轮次（澄清了产品关键机制）不命中「里程碑/决策/话题转向/收尾」任一判据，按协议字面不写是合规的——但用户期望这类有价值轮次也沉淀；
2. **宿主强指令竞争**：CodeBuddy 系统提示有强指令「每次实质工作后 MUST 写 .codebuddy/memory/」，而协议块措辞软（「命中任一即沉淀」）且位于文件尾部，两条记忆协议竞争时强指令赢了，产生「已沉淀」错觉；
3. **会话中无提醒载体**：hook 只在 SessionStart 注入任务关联流程（`codewiki/hooks/task_session_start.py:357-412`），主动沉淀全靠 AGENTS.md 静态文本被动等待判据命中，没有每轮自查动作。

## 决策（已实施，测试全绿 122+109 passed）

改权威源 `codewiki/mcp/prompts.py` 的 `_active_settle_section()`（非只改 AGENTS.md，会被 install-hooks 覆盖打回）：

1. **判据扩面**：第 2 条从「关键技术决策落定」扩为「关键技术决策落定，或澄清/纠偏了产品机制、代码事实等关键认知」——纯 Q&A 价值轮次不再合规漏记；
2. **被动判据 → 主动自查**：加硬性动作「每轮回复收尾前自查上述判据，命中即写，不要依赖『想起来』」；
3. **双通道声明**：新增「宿主 IDE 自带的工作记忆（如 `.codebuddy/memory/`）与本协议的任务记忆是独立通道，写了前者不豁免后者」——消除「已沉淀」错觉。

## 根因

协议设计时假设判据命中 + 静态文本就够，低估了宿主平台自带记忆指令的竞争强度；且判据枚举漏掉了「澄清关键认知」这类最常见的价值轮次形态。
