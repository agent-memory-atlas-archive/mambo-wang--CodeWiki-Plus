---
type: pitfall
title: "Trae Windows hook 命令勿用 `||` 兜底——PowerShell 5.1 解析期报错导致 hook 静默不执行"
tags: ["pitfall", "powershell", "sessionstart"]
metadata:
  date: 2026-10-13
  confidence_level: weak
  task_id: Trae适配
  severity: high
  root_cause: "Trae Windows 用 PowerShell 5.1 执行 hook 命令，PS5.1 不支持 `||`（解析期错误整条命令不执行），且 Windows 通常无 python3；bash 风味的 `python3 ... || python ...` 兜底写法在该环境是死命令，失败被 IDE 静默吞掉。"
  reason: "调试根因已在本会话实证（PS5.1 解析错误复现 + 修复后逐事件仿真通过），按主动沉淀协议落草稿待确认"
status: draft
author: iamwangbao-163-com
generated: { by: codewiki/5.14.1, at: 2026-10-13T01:59:18Z }
stale_after: 2027-04-11
---

## 现象

Trae（Windows）项目级/全局 hook 配置了 `python3 xxx || python xxx` 形式的命令后从未触发：无 SessionStart 注入、无日志、无任何报错提示，表现为「不稳定/不生效」。

## 根因

Trae 在 Windows 上用 **PowerShell 执行 hook 命令**（官方文档：macOS/Linux 用 Bash，Windows 用 PowerShell）。Windows PowerShell 5.1 **不支持 `||`/`&&`**——且是**解析期错误**（`The token '||' is not a valid statement separator in this version`），整条命令直接不执行，不会进入任何一条分支。叠加 Windows 通常没有 `python3`（python.org 安装只给 `python`/`py`），`python3 ... || python ...` 这种 bash 风味兜底写法在 Trae Windows 上是死命令。非阻断性失败被 IDE 静默吞掉，所以表现为「毫无动静」。

## 结论/做法

- Trae Windows 的 hook command 必须是 **PowerShell 5.1 兼容语法**：直接写 `python ".trae/hooks/xxx.py"`（或 `py ...`）；不要用 `||`/`&&` 做解释器兜底。
- 没有同时兼容 PowerShell 5.1 与 Bash 的单行兜底语法；跨平台仓库要么按平台各配一份，要么统一用 `python`（macOS/Linux 需保证 `python` 可用）。
- 排查同类「hook 没反应」问题的固定动作：①把 command 原样拷到本机 PowerShell 跑一遍看是否解析错误；②模拟事件 JSON 管道给脚本验证 stdin/stdout；③IDE 侧 设置 > Hooks > 运行日志 看 Agent Hooks 日志。

实证：2026-10-13 CodeWiki-Plus 仓库 .trae/hooks.json 三条 hook（SessionStart/Stop/UserPromptSubmit）因同一原因全部从未执行，改为 `python ...` 后模拟 Trae 事件验证通过。
