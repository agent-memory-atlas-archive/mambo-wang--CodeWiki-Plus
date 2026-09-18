---
type: pitfall
title: "全局 codewiki.exe 无法 import 本地包：install-hooks 需用 python -m codewiki.cli.main 从仓库根执行"
tags: ["codewiki", "modulenotfounderror", "pitfall"]
metadata:
  date: 2026-09-18
  confidence_level: weak
  source_session: "7245f28d19714f71bca1abdd87568f23"
  related_modules: ["cli"]
  severity: medium
  source_ref: "conversations/conv-user_command-commands-codewiki-启用-禁用任务管理（跨会话任务记忆）-管理-team-me.md"
  scene: "hook 接线 / CLI 使用"
status: draft
author: iamwangbao-163-com
generated: { by: codewiki/5.10.1, at: 2026-09-18T00:59:36Z }
stale_after: 2027-03-17
origin: conversation

---

## 背景

在 CodeWiki 源码 checkout 内执行 `codewiki install-hooks --repo-path d:\repos\CodeWiki-Plus` 时，PATH 上的全局 `codewiki.exe` 报 `ModuleNotFoundError: No module named 'codewiki'`。

## 原因

console script 的 `sys.path` 不含当前工作目录，且 `codewiki` 包未 pip 安装到全局环境，全局 exe 找不到本地源码包。

## 正确做法

从仓库根目录改用等价模块入口执行（`codewiki/cli/main.py` 有 `__main__` 守卫）：

```powershell
python -m codewiki.cli.main install-hooks --repo-path d:\repos\CodeWiki-Plus
```

这样 `codewiki` 解析到本地源码，功能与 CLI 完全等价。
