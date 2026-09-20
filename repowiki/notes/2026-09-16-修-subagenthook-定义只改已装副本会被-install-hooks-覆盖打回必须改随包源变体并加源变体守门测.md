---
type: pitfall
title: 修 subagent/hook 定义只改已装副本会被 install-hooks 覆盖打回：必须改随包源变体并加源变体守门测试
tags:
- pitfall
- readfile
aliases:
- toolsMCP 无效
- distill-worker 空转
- 修复被覆盖打回
- 源变体守门测试
- install-hooks 覆盖拷贝
- mcpServers 授权
- 改源副本还是项目副本
metadata:
  date: 2026-09-16
  confidence_level: weak
  task_id: 产品维护
  related_modules:
  - agents
  - hooks
  - cli
  severity: high
  root_cause: 'install_hooks 对 agent 定义是强制覆盖拷贝、项目副本没有回写机制；tests/test_install_hooks.py
    的断言又把错误 schema 固化成契约（原为 assert "toolsMCP: codewiki" in installed），ide_config.py
    注释还把错误 schema 写成各宿主契约——三处叠加让上游修复无法存活。'
status: stable
author: iamwangbao-163-com
generated:
  by: codewiki/5.10.1
  at: 2026-09-16 13:47:04+00:00
stale_after: '2027-03-19'
verified:
- by: human:wangbao
  at: '2026-09-20T02:38:17Z'
---

## 背景

2026-09-16 排查「补蒸馏 subagent 空转」时发现：`distill-worker` frontmatter 的 bug（`tools: ReadFile` 白名单 + 非官方字段 `toolsMCP`）在 `notes/2026-09-08-蒸馏-worker-启动前先自检-mcp-可见性拿不到-distill-conversation-就停不要退让直连-ha.md` 里已有 2026-09-11 的实测定案与修法，但本仓库 `codewiki/agents/distill-worker.md` 与 `.codebuddy/agents/distill-worker.md` 里**仍是旧 schema**——上游修过，没落到源码。

## 现象

subagent 能被 spawn，但 **0 tool uses**、空转、只回一句话；`distill_conversation(mode="prepare")` 从未被调用，补蒸馏整条链路静默失效。

## 正确做法

1. **修复必须改随包发布的源变体**：`codewiki/agents/distill-worker.md`（CodeBuddy 家族，用 `mcpServers: [codewiki]` 且**省略 `tools:`**）与 `codewiki/agents/distill-worker.claude.md`（claude 家族，省略 tools 行继承全部工具）。`.codebuddy/agents/`、`.qoder/agents/`、`.trae/agents/` 只是 `install-hooks` 的**强制覆盖拷贝目标**，改副本会被下一次接线打回；改完用哈希核对副本与源一致。
2. **加源变体守门测试**：在 `tests/test_install_hooks.py` 直接断言源变体（不含 `toolsMCP`、不含 `tools:` 白名单、含 `mcpServers`），并修正把错误 schema 固化成契约的既有断言。
3. **让失败可见**：worker 剧本里确认「第一步 prepare 即探活，工具不可见就立即停下上报，不重试、不退让 python 直连」——否则失败会静默成“积压已清空”。

## 根因（三处叠加，造成“看起来已修好”）

1. `install_hooks` 对 agent 定义是覆盖拷贝，项目副本没有回写机制；
2. 测试断言把 bug 锁成契约——改源码反而会让测试变红；
3. `codewiki/cli/utils/ide_config.py` 的注释把错误 schema 写成各宿主契约（文档层面的假事实）。

再加一层：IDE 的 subagent 注册表是**启动时快照**，改完当次会话无法验证（仍用旧定义），必须新会话观察 tool uses 数才能确认。

## 适用范围

任何“源副本 + 项目副本”双份维护、且存在 install/copy 流程的配置与脚本（`codewiki/agents/*`、`codewiki/hooks/*`、`codewiki/hooks.yaml`，以及 `install-hooks` 的任何拷贝目标）。判断信号：同一文件在仓库里存在两份，且有覆盖式安装器。

