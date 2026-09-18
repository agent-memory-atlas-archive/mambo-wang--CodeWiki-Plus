---
type: lesson
title: "宿主 IDE 工作记忆与 CodeWiki 任务记忆是独立通道，写前者不豁免后者"
tags: ["codebuddy", "codewiki", "lesson"]
metadata:
  date: 2026-09-18
  confidence_level: weak
  task_id: 产品维护
  source_session: "21b7dedf054c44bfbec90d72f16ba0b4"
  related_modules: ["task-manager", "knowledge-loop"]
  severity: medium
  source_ref: "conversations/conv-working_memory_content-The-following-is-the-existing-working-2-e83954.md"
  scene: "产品维护-记忆沉淀"
status: draft
author: iamwangbao-163-com
generated: { by: codewiki/5.10.1, at: 2026-09-18T06:16:13Z }
stale_after: 2027-03-17
origin: conversation

---

## 背景

用户发现记忆都沉淀到了 `.codebuddy/memory/2026-09-18.md`，没有进 `repowiki/tasks/产品维护/memories/`，质疑任务关联是否生效。

## 正确做法

两套记忆系统完全独立，停顿点必须**两条都写**：

| 通道 | 位置 | 性质 | 写入方式 |
|------|------|------|---------|
| CodeBuddy 工作记忆 | `.codebuddy/memory/*.md` | IDE 宿主强制机制，跨会话工作日志 | 每次实质工作后必须追加，无法关闭 |
| CodeWiki 任务记忆 | `repowiki/tasks/<任务>/memories/<user_id>.md` | 任务级进度知识，`get_task_context` 注入 | 自然停顿点用 `add_task_memory(task_id=...)` 直写 |

写了 IDE 工作记忆后会产生「已记录」的错觉，漏掉任务记忆通道——这是实际发生过的遗漏，不是理论风险。

## 根因

宿主平台注入的记忆指令（强 MUST）与项目协议块（软措辞）竞争，Agent 执行了强指令后短路径认为「沉淀已完成」。修复已进 ACTIVE-SETTLE 块（双通道独立声明），但 Agent 在停顿点仍应显式自查两条通道是否都写了。
