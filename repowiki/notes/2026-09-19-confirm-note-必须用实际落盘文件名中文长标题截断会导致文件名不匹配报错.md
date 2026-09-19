---
type: pitfall
title: "confirm_note 必须用实际落盘文件名：中文长标题截断会导致文件名不匹配报错"
tags: ["pitfall", "powershell"]
metadata:
  date: 2026-09-19
  confidence_level: weak
  task_id: 他山之石
  source_session: "c07baaa505eb4d5e8a426636266c63a0"
  related_modules: ["knowledge-loop"]
  severity: medium
  source_ref: "conversations/conv-working_memory_content-The-following-is-the-existing-working-788cb5.md"
  scene: "草稿笔记确认"
status: draft
author: iamwangbao-163-com
generated: { by: codewiki/5.10.1, at: 2026-09-19T01:17:55Z }
stale_after: 2027-03-18
origin: conversation

---

## Background

批量 confirm_note 确认草稿笔记时，凭笔记标题记忆构造 `note_file` 参数，其中 1 条报错——中文长标题经 slug 化/截断后的实际文件名与构造值不一致。

## 正确做法

confirm 前先用 `search_file`（如 `*关键词*` 模式）查出实际落盘文件名，再以实际文件名调用 confirm_note；批量确认时逐条核对，失败项单独查名重试，不要凭标题拼接文件名。

## Root cause

笔记落盘文件名由标题经确定性变换（去停用词、截断、slug 化）生成，中文标题的变换结果不易人工预测；`note_file` 参数要求与实际文件名完全一致。

## 适用范围

所有 confirm_note / reject_note / 指定 note_file 的评审操作，中文标题笔记尤其如此。与『distill_conversation submit 的 distilled 必须是映射形状』、『Windows PowerShell 下 git add 中文路径静默失败』主题不同：本条讲的是评审操作的文件名参数坑。
