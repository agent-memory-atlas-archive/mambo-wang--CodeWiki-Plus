---
type: decision
title: distill-worker subagent 定义随包发布，hook 启用时自动拷贝到项目 .codebuddy/agents/
tags:
- codewiki
- decision
metadata:
  date: '2026-08-23'
  task_id: 产品维护
  related_modules:
  - mcp
  - agents
  - wiki/scenarios/IDE-Hook采集链路方法.md
  severity: medium
  source_ref: conversations/conv-开始新对话触发选择任务后，会有query_wiki以及蒸馏操作，这些操作可以放到subagent执行吗，别影响用户正常使-ad2869.md
  scene: 产品维护-蒸馏机制
  consolidated_into: ''
  confidence_level: weak
status: stable
generated:
  by: codewiki/5.3.0
  at: '2026-08-23 12:10:38+00:00'
stale_after: '2027-08-26'
origin: conversation
verified:
- by: human:wangbao
  at: '2026-08-25T16:48:21Z'
author: mambo-wang
source_conversations: ['conversations/conv-user_command-commands-codewiki-启用-禁用任务管理（跨会话任务记忆）-管理-team-me.md']

---

## Background

会话启动补蒸馏已改为委托「蒸馏 worker」subagent（distill-worker.md）执行。此前该定义文件只手工放在项目 `.codebuddy/agents/` 下，用户要求把定义文件存入 CodeWiki 源码目录，并在启用 hook 时自动拷贝到目标项目，避免每个项目手工复制、版本漂移。

## Decision/正确做法

`distill-worker.md` 的权威版本只存在 **`codewiki/agents/distill-worker.md`**（随 `codewiki` 包发布），任何项目启用 hook 时自动拷贝到目标项目的 `.codebuddy/agents/distill-worker.md`，与 `hooks/*.py` 的安装方式完全对称。具体落地：

1. 源码副本：`codewiki/agents/distill-worker.md`，与项目内 `.codebuddy/agents/distill-worker.md` 内容一致，包内为权威版本。
2. hook 启用时自动拷贝（`codewiki/mcp/prompts.py` 两处）：`_prompt_init_wiki`（init 流程）与 `_prompt_team_memory_hook`（步骤 2A）——创建 `.codebuddy/agents/` 目录、从包内 `agents/distill-worker.md` 强制拷贝、校验命令增加 `assert` 确认 md 存在且以 `---` 开头、回退逻辑（`CODEWIKI_HOME`）同步支持 agents 拷贝。
3. 关闭步骤 2B 说明：`distill-worker.md` 可保留也可删除，重新启用自动补回。
4. 打包声明：`pyproject.toml` 的 `package-data` 增加 `"agents/*.md"`——否则 pip 安装时非 `.py` 文件默认不打包，`.md` 不会随包发布。

## Rationale

subagent 定义与 hook 脚本同属「启用即部署」的配套资源，与 `hooks/*.py` 走同一安装路径可降低维护成本；源码只存一份避免双副本漂移。

## 验证

- `prompts.py` 语法 OK；`tests/test_task_session_start.py` 4 个测试全部通过；无 lint 错误。
- ~~待验证点：`distill-worker.md` 的 frontmatter（`toolsMCP` 字段名、agentic 模式下 Task 工具是否能直接 spawn）依赖 IDE 对 subagent 定义的解析，需在下次新会话观察 hook 是否成功把蒸馏委托出去；若解析方式有差异只需调整该文件 frontmatter 字段名，不影响其他改动。~~
- **已验证（2026-09-16）**：`toolsMCP` 是**非官方字段、静默无效**，且 `tools: ReadFile` 白名单会把 MCP 工具一并挡掉——两者叠加正是 worker「0 tool uses 空转」的根因。现写法改为 `mcpServers: [codewiki]` 并省略 `tools` 行。另注：修复必须改随包源变体（`codewiki/agents/*.md`），只改 `.codebuddy/agents/` 已装副本会被 `install-hooks` 强制覆盖打回。详见 `notes/2026-09-08-蒸馏-worker-启动前先自检-mcp-可见性拿不到-distill-conversation-就停不要退让直连-ha.md`。修复丢失的完整机制（覆盖拷贝 + 测试固化 + 文档假事实）见 `notes/2026-09-16-修-subagenthook-定义只改已装副本会被-install-hooks-覆盖打回必须改随包源变体并加源变体守门测.md`。

## distill-worker.md 按智能体分流不同源变体：比对漂移前先查 IDE_SPECS.agent_file

> 合并自蒸馏候选：distill-worker.md 按智能体分流不同源变体：比对漂移前先查 IDE_SPECS.agent_file

## 背景

检查各智能体目录下 `agents/distill-worker.md` 是否与源文件一致时，若统一与 `codewiki/agents/distill-worker.md` 对比，会误报 `.qoder`/`.trae` 存在 15 行「漂移」。

## 正确做法

各智能体的 subagent 文件来源按 `IDE_SPECS.agent_file` 分流（依据代码核对：`codewiki/cli/utils/ide_config.py:55-106`）：

| 目标 | 正确源变体 |
|---|---|
| `.codebuddy/agents/distill-worker.md` | `codewiki/agents/distill-worker.md`（CodeBuddy frontmatter：`tools: ReadFile` + `toolsMCP`） |
| `.qoder/agents/distill-worker.md` | `codewiki/agents/distill-worker.claude.md`（claude 家族变体，省略 tools 行以继承全部工具含 MCP） |
| `.trae/agents/distill-worker.md` | 同上 |

比对漂移前先确认该智能体对应的源变体，再下结论；重跑 `install-hooks` 属幂等操作，可安全用于强制同步。
