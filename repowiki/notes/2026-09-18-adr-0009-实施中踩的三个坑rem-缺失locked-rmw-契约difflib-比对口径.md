---
type: lesson
title: "ADR-0009 实施中踩的三个坑：re.M 缺失、locked_rmw 契约、difflib 比对口径"
tags: ["id", "lesson"]
metadata:
  date: 2026-09-18
  confidence_level: weak
  source_session: "44b4bea9c40947d09554371636e88cac"
  related_modules: ["team-memory-fusion", "mcp"]
  severity: medium
  source_ref: "conversations/conv-user_command-commands-codewiki-启用-禁用任务管理（跨会话任务记忆）-管理-team-me-3.md"
  scene: "任务记忆治理实施"
status: draft
author: iamwangbao-163-com
generated: { by: codewiki/5.10.1, at: 2026-09-18T01:11:06Z }
stale_after: 2027-03-17
origin: conversation

---

## 背景

ADR-0009（supersede + 写入检查）实施过程中测试暴露三个非显而易见的 bug，全部是「实现看起来对但行为错」的类型。

## 三个坑与修法

1. **`_SUPERSEDED_RE` 忘加 `re.M`**：标记行 `> [superseded ...]` 在条目**第二行**，`^` 只匹配字符串开头，`entry_is_superseded` 永远返回 False，过滤完全失效。多行文本匹配 `^`/`$` 必须带 `re.M`。
2. **`locked_rmw` 契约误用**：transform 返回 None = 中止写入（错误）、返回字符串 = 新文件内容。把错误信息当字符串返回，会被当成新文件内容**写盘**。修法：错误路径用异常（`_SupersedeError`）穿出，外层捕获转错误字符串。
3. **difflib 比对口径**：① 比对含 `### 时间戳 #id` 头会稀释 ratio，真重复漏拦——剥离头部只比正文；② 短文本（如「记忆0」vs「记忆1」）一字之差 ratio≈0.9 即超阈值误拦——<20 字符豁免去重。

## 教训

行为类改动必须配验收测试先行暴露（本次 4 个失败测试中 2 个暴露的是实现 bug 而非测试错误）；「看起来对」的字符串/正则/相似度逻辑要用最小复现脚本直接验证。
