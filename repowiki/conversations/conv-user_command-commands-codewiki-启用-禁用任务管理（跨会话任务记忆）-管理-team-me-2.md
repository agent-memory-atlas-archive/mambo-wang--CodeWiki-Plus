---
type: Conversation
title: "conversation 20260917T114342Z"
status: distilled
stale_after: 2026-12-16
generated: { by: codewiki/5.10.1, at: 2026-09-17T11:43:42Z }
captured_at: "2026-09-17T11:43:42Z"
content_hash: "sha256:0b1e16baeb73b68b1803466cdb720dd493f7be19638e853ac4a0c07992440ec8"
friction_score: 0
friction_signals: "correction=1,interrupt=0,repeat=0,user_turns=3"
keep_raw: false
link_to: ""
source_session: "27fd7bc470f54eb7978afaf446b80df5"
task_id: "产品维护"
turn_count: 39
---

# Conversation Transcript

user: <user_command>
--- commands: codewiki/启用/禁用任务管理（跨会话任务记忆）--- 
 管理 team-memory fusion 的对话自动采集 Hook。

**支持范围由 `codewiki/hooks.yaml` 注册表驱动**（家族归并：claude / cursor / codex / trae 四种 hook 格式）：
- **已验证支持**（日常使用背书）：`codebuddy`, `qoder`, `claude-code`, `trae`, `qwenwork`
- **理论支持**（家族归并推导，未经真机验证，接线后必须跑步骤 2A 第 5 步的模拟事件验证）：`cursor`, `codex-cli`, `gemini-cli`, `windsurf`, `kilocode`, `opencode`

用户请求：**启用**采集 Hook。执行步骤 1 确认现状后直接进入步骤 2A。

采集 Hook 只负责把对话捕获到 `repowiki/raw/`（仅采集、不蒸馏）；蒸馏是独立的显式步骤，见 distill-conversations prompt。

**当前项目探测结果**：`d:\repos\CodeWiki-Plus` 下检测到的智能体配置目录：`codebuddy`, `qoder`, `trae`。**只为探测到的智能体接线**——探测不凭空创建任何目录；用户想接未探测到的智能体时，由用户自行初始化该工具的配置目录后重跑本流程。

claude 家族（CodeBuddy/Qoder/Claude Code/Gemini CLI 及理论支持工具）接线格式一致（各自 `settings.json`，事件 SessionStart/SessionEnd），仅配置目录不同。cursor 家族（`hooks.json` + 事件名 sessionStart/stop）与 codex 家族（`hooks.json` 嵌套结构）格式不同，且 **cursor 家族采集降级**：stop 事件不携带 transcript_path，无正文可采（仅事件级诊断、不落盘）、无法完整蒸馏对话——为 cursor 家族接线前须向用户说明此限制。trae 家族（TRAE，`hooks.json` + 事件名 SessionStart/Stop/UserPromptSubmit，顶层 `{"version": 1, "hooks": {...}}`）已真机验证：SessionStart/UserPromptSubmit 完整可用，但 TRAE 无 SessionEnd 事件——Stop 每轮 Query 结束触发且不携带 transcript_path（仅 last_assistant_message），**采集同样降级（无正文可采，仅事件级诊断、不落盘）**，对话捕获依赖 AGENTS.md「会话收尾轮」norm 由 Agent 中介补漏——为 trae 家族接线前须向用户说明此限制。

## 步骤 1: 检查当前状态
依次检查项目根目录下**探测到的**每个智能体配置目录（如 `d:\repos\CodeWiki-Plus/.codebuddy/`、`d:\repos\CodeWiki-Plus/.qoder/`、`d:\repos\CodeWiki-Plus/.claude/` 等，以探测结果为准）：
- 每个目录下读取家族对应的配置文件（claude 家族 `settings.json`；cursor/codex/trae 家族 `hooks.json`）：**已启用** = 存在 SessionEnd 与 SessionStart（或家族对应事件名，trae 家族为 Stop）两个条目，且对应目录 `hooks/` 下 `capture_session_end.py` 与 `task_session_start.py` 两个脚本文件都物理存在（claude 家族 command 用项目相对路径如 `python ".qoder/hooks/task_session_start.py"`——宿主以项目根为工作目录执行命令；不写机器相关绝对路径、也不用 `$*_PROJECT_DIR` 变量（实测不可靠）；历史绝对路径条目可视为已启用，但建议重跑接线迁移为相对路径形式）
- 向用户报告哪些智能体已启用、哪些未启用

## 步骤 2A: 启用
**首选路径：运行 CLI 自动检测接线（推荐，覆盖全部已探测到的智能体）**

```powershell
codewiki install-hooks --repo-path d:\repos\CodeWiki-Plus
```

CLI 会自动检测项目根目录下存在哪些智能体配置目录（按 `codewiki/hooks.yaml` 注册表探测），检测到哪些就为哪些自动完成全部接线：
- 强制拷贝 hook 脚本与 `distill-worker.md` 到对应 `.codebuddy|.qoder|.claude|.gemini|.trae/hooks/` 与 `agents/`
- 幂等合并 `settings.json`（TRAE 为 `.trae/hooks.json`：顶层补 `version: 1`，SessionEnd 注册映射为 Stop 且不写 matcher）的 SessionStart/SessionEnd 注册（保留已有无关配置，重复运行不产生重复条目）
- 向 `AGENTS.md` upsert 任务记忆引导段（多 IDE 共享一份，只写一次）

CLI 不可用（`codewiki` 命令未安装）时，回退到下方手动步骤。手动接线时以 `.codebuddy` 为例，**Qoder / Claude Code / Gemini CLI 仅目标目录不同**：`.codebuddy/` ↔ `.qoder/` ↔ `.claude/` ↔ `.gemini/`（settings.json、hooks/、agents/ 的相对位置与内容完全一致，command 均为项目相对路径）。**仅为步骤 1 探测到的智能体执行手动接线；未探测到的智能体一律不接、不创建其目录**——本机安装了某工具不等于本仓库在用它，除非用户明确点名并确认。

### 手动兜底步骤
1. **确保两个 hook 脚本与 distill-worker subagent 就位（每次都强制覆盖拷贝）**。脚本必须物理存在于目标项目，IDE 不会自动创建它们。
   **不论目标是否已存在，每次启用都要从 CodeWiki 自带的源文件重新复制覆盖**，
   以保证与目标 `codewiki` 包版本一致（不要因为"已存在"就跳过，否则升级包后会残留旧脚本）：
   用以下命令解析 CodeWiki 自带的源文件路径，并**强制复制**到目标目录
   （务必复制，不要凭记忆重写，以免与 `codewiki` 包行为不一致）：

     ```powershell
     # 源文件随 codewiki 包发布：codewiki/hooks/ 下两个 hook 脚本 + codewiki/agents/distill-worker.md
     $pkg = python -c "import codewiki, os; print(os.path.dirname(codewiki.__file__).replace('\\','/'))"
     $destDir = Join-Path 'd:\repos\CodeWiki-Plus' '.codebuddy/hooks'
     $agentDir = Join-Path 'd:\repos\CodeWiki-Plus' '.codebuddy/agents'
     New-Item -ItemType Directory -Force -Path $destDir | Out-Null
     New-Item -ItemType Directory -Force -Path $agentDir | Out-Null
     Copy-Item (Join-Path $pkg 'hooks/capture_session_end.py') (Join-Path $destDir 'capture_session_end.py') -Force
     Copy-Item (Join-Path $pkg 'hooks/task_session_start.py') (Join-Path $destDir 'task_session_start.py') -Force
     Copy-Item (Join-Path $pkg 'agents/distill-worker.md') (Join-Path $agentDir 'distill-worker.md') -Force
     python -c "import ast; ast.parse(open(r'$destDir/capture_session_end.py', encoding='utf-8').read()); ast.parse(open(r'$destDir/task_session_start.py', encoding='utf-8').read()); assert open(r'$agentDir/distill-worker.md', encoding='utf-8').read().startswith('---'), 'distill-worker.md missing'; print('hook scripts + distill-worker.md copied OK')"
     ```

     若 `import codewiki` 失败（未 pip 安装且不在源码 checkout 内），回退：从
     `CODEWIKI_HOME` 环境变量指向的 checkout 取
     `$env:CODEWIKI_HOME/codewiki/hooks/` 下的两个脚本与
     `$env:CODEWIKI_HOME/codewiki/agents/distill-worker.md`，同样 Copy-Item 到 `$destDir` / `$agentDir`。
     兜底都不满足时，提示用户先 `pip install codewiki` 或设置 `CODEWIKI_HOME`，不要凭记忆写脚本。
     **为 Qoder/Claude Code 接线时，把上面 `$destDir` / `$agentDir` 中的 `.codebuddy` 换成 `.qoder` / `.claude` 即可。**
2. 创建或合并 `d:\repos\CodeWiki-Plus/.codebuddy/settings.json`，加入以下 hook 注册（保留文件中已有的无关配置；Qoder/Claude Code/Gemini CLI 写入 `.qoder/settings.json` / `.claude/settings.json` / `.gemini/settings.json`，command 中目录名随配置目录变化，其余完全一致）。**command 用项目相对路径（宿主以项目根为工作目录执行命令），不写机器相关绝对路径、也不用 `$*_PROJECT_DIR` 变量（各宿主变量展开经实测不可靠）**——settings.json 随仓库共享，绝对路径提交后队友克隆到其他目录即失效：

```json
{
  "hooks": {
    "SessionStart": [
      { "matcher": "startup", "hooks": [ { "type": "command", "command": "python \".codebuddy/hooks/task_session_start.py\"", "timeout": 15 } ] }
    ],
    "SessionEnd": [
      { "matcher": "other", "hooks": [ { "type": "command", "command": "python \".codebuddy/hooks/capture_session_end.py\"", "timeout": 30 } ] }
    ]
  }
}
```

   - `SessionStart`（matcher=`startup`）：新会话开始同步返回 `hookSpecificOutput.additionalContext`，把任务关联引导注入给 Agent，是"新建会话提示选任务"的确定性触发点；如需覆盖 `--resume` 恢复场景，matcher 改为 `startup|resume`。
   - `SessionEnd`：唯一可靠携带 `transcript_path` 的事件，能抓到完整正文。
   `PreCompact`/`Stop` 不带 transcript，无正文可采（hook 只输出 stderr 诊断、不落盘），故不注册。

2b. **TRAE（trae 家族）变体**：写入 `d:\repos\CodeWiki-Plus/.trae/hooks.json`（不是 settings.json），顶层多一个 `version` 字段，SessionEnd 换成 `Stop`（TRAE 无 SessionEnd 事件），且不写 matcher（TRAE 的 matcher 仅对 PreToolUse/PostToolUse/Notification 有效）：

```json
{
  "version": 1,
  "hooks": {
    "SessionStart": [
      { "hooks": [ { "type": "command", "command": "python \".trae/hooks/task_session_start.py\"", "timeout": 15 } ] }
    ],
    "Stop": [
      { "hooks": [ { "type": "command", "command": "python \".trae/hooks/capture_session_end.py\"", "timeout": 30 } ] }
    ],
    "UserPromptSubmit": [
      { "hooks": [ { "type": "command", "command": "python -m codewiki.mcp._ide_hook --enable", "timeout": 10 } ] }
    ]
  }
}
```

   注意 TRAE 的 Stop 每轮 Query 结束都触发（非会话级）且不携带 transcript_path——hook 采集无正文可采（仅 stderr 诊断、不落盘），对话捕获依赖 AGENTS.md「会话收尾轮」norm 由 Agent 中介采集补漏。接线前须向用户说明此降级。TRAE 环境变量注入 `TRAE_PROJECT_DIR` 与 `CLAUDE_PROJECT_DIR`，脚本已支持。

3. 向 `d:\repos\CodeWiki-Plus/AGENTS.md` 写入任务记忆会话引导段（启用采集后，新建会话时 Agent 才会提示用户关联/新建任务）。
   **只动标记块，绝不改 AGENTS.md 其余内容**：若已存在 `<!-- TEAM-MEMORY-TASK:START -->` 到 `<!-- TEAM-MEMORY-TASK:END -->` 之间的块，用下面文本整体替换；若不存在，追加到文件末尾（前面留一个空行）。以下文本按原样写入，含 START/END 注释标记：

<!-- TEAM-MEMORY-TASK:START -->
## Task memory (任务记忆)

跨会话延续长线工作上下文。任务记忆是**任务范围内的进度知识**（本次做了什么、下一步、待办），与 Wiki 笔记（**跨任务的通用经验**）互补。

**会话开始时（必须执行）：**
1. `list_tasks(status="active")` 列出进行中的任务
2. **必须用 `ask_followup_question` 弹框，且只弹一次、一框列全**：只调用 1 次，questions 数组只放 1 个 question（标题「任务关联」，multiSelect=false），options 一次性列出「每个进行中任务」+「新建任务…（在输入框直接输入名称）」+「跳过」。**严禁**因工具 schema 建议 2-4 个 options 就拆成多个 question 或分多次弹框；唯一例外是用户选了「新建任务…」却没给名字，可再弹一次要名字
3. 用 `set_session_task(source_session_id=<会话id>, task_id=<任务id>)` 绑定；列表里没有的任务名先 `create_task(title=<任务名>)` 再绑定；用户选「跳过」则本次不关联
4. `get_task_context(task_id=<选中任务>)` 拉取任务描述 + 记忆 + 关联笔记
5. `pending_raw_count > 0` 时**阻塞式补蒸馏，先记忆后回答**：发一个阻塞式 subagent 补蒸馏，**清空本任务的全部待蒸馏积压**（不设条数上限——只挑最近几条会让老积压永远轮不到），任务记忆与经验一次产出；完成后重新 `get_task_context` 拉取最新记忆再回答用户。subagent 失败/超时不重试——带旧记忆直接回答，未蒸馏的 raw 留在 raw/ 等下次会话再补。蒸馏产出的草稿笔记须 `confirm_note` 确认后才落盘；任务记忆直写、无需确认（ADR-0002）
6. **项目定向（按条件执行）**：若本会话上下文中**没有**已注入的 Team Doctrine / 知识库概览（hook 档宿主的 SessionStart 注入会带上；注入文件随项目上下文自动加载的宿主没有此注入），调用 `query_wiki(mode="overview")` 拉取一次；已注入则跳过，绝不重复拉取
7. **会话收尾（按条件执行）**：检查本文件是否存在 **CODEWIKI-ACTIVE-SETTLE 块**（HTML 注释标记包裹的独立小节，见下方条件）：
   - **存在**：按该块执行——自然停顿点命中四判据即直写沉淀（任务记忆 `add_task_memory` / 通用经验 `ingest_note(status="draft")`），收尾轮做带 `active_settle=true` 标记的保险采集；**跳过**下方传统收尾轮采集
   - **不存在**：按下方**传统收尾轮采集**执行

**传统收尾轮采集（任务完成 / 用户道别 / 用户显式要求记录时）：**
将本会话对话重建为 `[{role, content}]` 列表，调用 `capture_conversation(conversation=..., source_session_id=<本会话id>, task_id=<任务id>)` 落 raw。**user 消息必须逐字保留**（需求/纠正/决策是知识的主要来源），assistant 保留关键结论原句，工具调用略去。同一会话多次收尾采集会被 supersede 替换，不会堆积。

完整工作流、存储布局与实现约束见 MCP prompt：`get_prompt(name="task-workflow")` —— 按需获取，不在此重复。
<!-- TEAM-MEMORY-TASK:END -->

4. 前置条件：hook 启动的 python 进程必须能 import `codewiki` 包。满足任一即可：codewiki 已通过 pip 安装；hook 位于 CodeWiki 源码 checkout 内；或设置了 `CODEWIKI_HOME` 环境变量指向 checkout。都不满足时 wrapper 会跳过采集并输出带操作指引的 systemMessage（绝不阻塞 IDE）
5. 用模拟事件验证两个脚本（Qoder/Claude Code 用对应目录路径替换 `.codebuddy`；TRAE 的会话结束事件是 Stop，不带 transcript_path，见下方 TRAE 变体）：
   - SessionEnd（先准备一个小的 transcript 文件，如 `[{"role":"user","content":"测试"}]` 存为 d:/tmp/conv.json；期望 stdout 返回 `{"continue": true, "systemMessage": "team-memory capture started in background"}`）：wrapper 是 fire-and-forget，只回报「后台采集已启动」，**不回报采集结果**；是否真的落盘要等 1-2 秒后看 `d:\repos\CodeWiki-Plus/repowiki/raw/` 是否新增 `conv-*.md`（`source_session` = verify-1）。stdin 事件缺失或 JSON 非法时返回 `team-memory capture skipped: ...`，不会谎报成功。拼 `cwd` 时别写反斜杠路径（`d:
epos` 里的 `
`/`\C` 是非法 JSON 转义，事件会被整体丢弃）：

```powershell
'{"session_id":"verify-1","transcript_path":"d:/tmp/conv.json","cwd":"d:\repos\CodeWiki-Plus","hook_event_name":"SessionEnd","reason":"other"}' | python "d:\repos\CodeWiki-Plus/.codebuddy/hooks/capture_session_end.py"
```

   - SessionStart（期望 stdout 的 hookSpecificOutput.additionalContext 中包含"任务关联"）：

```powershell
'{"session_id":"verify-2","cwd":"d:\repos\CodeWiki-Plus","hook_event_name":"SessionStart","source":"startup"}' | python "d:\repos\CodeWiki-Plus/.codebuddy/hooks/task_session_start.py"
```

   - TRAE Stop（期望 stdout 的 systemMessage 正常返回、`repowiki/raw/` **不**新增任何文件——TRAE 无 SessionEnd/transcript_path，hook 无正文可采、不落盘，这是采集降级的预期行为；对话捕获由 Agent「会话收尾轮」norm 承担）：

```powershell
'{"session_id":"verify-3","hook_event_name":"Stop","stop_hook_active":false,"loop_count":0,"last_assistant_message":"done"}' | python "d:\repos\CodeWiki-Plus/.trae/hooks/capture_session_end.py"
```

6. 验证完成后删除测试产物：`d:\repos\CodeWiki-Plus/repowiki/raw/` 下 verify-1 会话生成的 conv-*.md 文件

## 步骤 2B: 关闭
**首选路径：运行 `codewiki install-hooks --repo-path d:\repos\CodeWiki-Plus --ide <name>` 可重新接线；关闭采集时**：
1. 依次检查探测到的各智能体目录（`.codebuddy/`、`.qoder/`、`.claude/`、`.gemini/` 等），从对应 `settings.json` 移除 SessionStart 与 SessionEnd 两个条目（其他 hook 保持不变；`"hooks": {}` 留空也可以）
2. 从 `d:\repos\CodeWiki-Plus/AGENTS.md` 移除任务记忆会话引导段：删除 `<!-- TEAM-MEMORY-TASK:START -->` 到 `<!-- TEAM-MEMORY-TASK:END -->` 之间的整段（含两行注释标记本身）；若不存在该标记块则无需处理，其余内容保持不动
3. **同步移除主动沉淀协议块**：从 `d:\repos\CodeWiki-Plus/AGENTS.md` 删除 `<!-- CODEWIKI-ACTIVE-SETTLE:START -->` 到 `<!-- CODEWIKI-ACTIVE-SETTLE:END -->` 之间的整段（含两行注释标记本身）；遗留的旧 `<!-- CODEWIKI-QWENWORK:START -->` 到 `<!-- CODEWIKI-QWENWORK:END -->` 块（若存在）一并删除。不存在的标记块无需处理，块外内容保持不动
4. 已采集的 raw 文件保留在 `repowiki/raw/`，之后仍可蒸馏；关闭采集不会删除它们
5. hook 脚本 `capture_session_end.py`、`task_session_start.py` 与 subagent 定义 `distill-worker.md` 可保留也可删除；重新启用时步骤 2A 会自动补回

## 注意事项
- Hook 接线支持范围见开头注册表清单（已验证：CodeBuddy/Qoder/Claude Code；理论支持按家族归并列出，接线后必须模拟事件验证）。完全不支持 hook 的运行时请改用 `capture_conversation` MCP 工具手动采集
- 仅在会话结束时（SessionEnd）采集一次，落到 repowiki/raw/conv-*.md；会话级 supersede 去重保证每个会话只保留最新一份完整 transcript，不会膨胀
- Hook 永不蒸馏、永不写 wiki 页面、永不使 IDE 失败（异常仅输出到 stderr，退出码保持 0）--- commands end ---
 
</user_command>

<working_memory_content>
The following is the existing working memory for this project. Use it as context.

# 长期记忆 (MEMORY.md)



## 环境偏好 / 约定



### npm 镜像源

- 当前环境（推测国内网络）使用 npm 官方源 `registry.npmjs.org` 下载**大体积原生二进制**（如 `@next/swc-darwin-x64`、better-sqlite3 预编译包）时速度极慢（<1KB/s，曾卡死 25+ 分钟）。

- 改用 `https://registry.npmmirror.com` 镜像源后速度约快 6 倍，全局安装 `npm install -g <pkg> --registry=https://registry.npmmirror.com` 是稳妥做法。

- 注意：npm 11 已不再识别 `--disturl` / `--prebuild-install-binary-host-mirror` 这类 CLI flag（会报 unknown config 警告），原生模块的二进制镜像需改用 `.npmrc` 配置。



## 已安装工具

- `omniroute`（AI 网关，v3.8.48，全局 npm 安装）：Dashboard `http://localhost:20128`，API `http://localhost:20128/v1`。编码工具 Base URL 指向 `/v1`、Model 用 `auto` 即可走免费后端。要求 Node ≥ 22.22.2（本机 v25.8.1 满足）。
</working_memory_content>

@command://codewiki/启用/禁用任务管理（跨会话任务记忆）  不对吧，这个命令的参数没有做国际化，显示的是key
assistant: [tool: ask_followup_question · {"questions": "[{\"header\": \"任务关联\", \"multiSelect\": false, \"options\": [{\"description\": \"task_id=CodeWiki-架构深化分析\", \"la…
user: <question>本次会话要关联哪个任务？（列表里没有想要的任务时，可直接在弹框的输入框里输入新任务名后回车）</question>
<answers>
产品维护
</answers>
</question_item>
</questions>
</question_answer>
assistant: [tool: mcp_get_tool_description · {"toolRequests": "[[\"codewiki\", \"set_session_task\"], [\"codewiki\", \"get_task_context\"]]"}]
assistant: [tool: mcp_call_tool · {"serverName": "codewiki", "toolName": "set_session_task", "arguments": "{\"source_session_id\": \"27fd7bc470f54eb7978afaf446b80df5\", \…
assistant: [tool: mcp_call_tool · {"serverName": "codewiki", "toolName": "get_task_context", "arguments": "{\"task_id\": \"产品维护\", \"repo_path\": \"d:\\\\repos\\\\CodeWik…
assistant: 任务已关联「产品维护」，无待蒸馏积压（pending_raw_count=0），直接处理你的问题。

你说的是这个 slash command 的参数（比如弹框里的选项/描述）没有走 i18n，显示的是 key。我先找到命令定义文件核实。

[tool: search_file · **/commands/**]

[tool: search_content · d:\repos\CodeWiki-Plus]
assistant: [tool: search_file · **/codewiki/*.md]

[tool: search_content · d:\repos\CodeWiki-Plus]
assistant: [tool: search_file · **/commands/codewiki/**]

[tool: list_dir · {"target_directory": "d:\\repos\\CodeWiki-Plus\\.codebuddy"}]
assistant: [tool: search_file · **/*.md]
assistant: [tool: search_content · d:\repos\CodeWiki-Plus]

[tool: search_file · **/commands/**]
assistant: [tool: search_content · d:\repos\CodeWiki-Plus\codewiki\mcp\prompts.py]
assistant: [tool: search_content · d:\repos\CodeWiki-Plus\codewiki\mcp\prompts.py]

[tool: search_content · d:\repos\CodeWiki-Plus\codewiki\mcp\locales\zh.yaml]
assistant: [tool: search_content · d:\repos\CodeWiki-Plus\codewiki\mcp\locales\en.yaml]

[tool: read_file · {"filePath": "d:\\repos\\CodeWiki-Plus\\codewiki\\mcp\\i18n.py"}]
assistant: [tool: search_content · d:\repos\CodeWiki-Plus\codewiki\mcp\prompts.py]
assistant: [tool: search_content · d:\repos\CodeWiki-Plus\codewiki\mcp\prompts.py]
assistant: 找到疑点了：`_PROMPT_REGISTRY` 里 `team-memory-hook` 注册了 4 个参数（action、repo_path、mode、active_settle，见 `codewiki/mcp/prompts.py:1668-1675`），而 zh.yaml 的 `team-memory-hook.args` 只看到 action 和 repo_path 两个。我核实一下两个语料文件和守门测试为什么没拦住。

[tool: search_content · d:\repos\CodeWiki-Plus\codewiki\mcp\locales\zh.yaml]

[tool: read_file · {"filePath": "d:\\repos\\CodeWiki-Plus\\tests\\test_i18n.py"}]
assistant: 问题定位到了。守门测试 `test_i18n.py` 只校验 zh↔en **互相**覆盖，没有校验 `_PROMPT_REGISTRY` 注册的参数在语料里存在。我确认一下 `team-memory-hook` 的注册参数与语料的差集，并检查是否还有其他 prompt 有同样缺口。

[tool: read_file · {"filePath": "d:\\repos\\CodeWiki-Plus\\codewiki\\mcp\\locales\\zh.yaml", "offset": 185, "limit": 40}]

[tool: read_file · {"filePath": "d:\\repos\\CodeWiki-Plus\\codewiki\\mcp\\prompts.py", "offset": 1600, "limit": 120}]
assistant: 现在读两份语料的完整 prompts 段，逐一比对注册表参数的覆盖情况。

[tool: read_file · {"filePath": "d:\\repos\\CodeWiki-Plus\\codewiki\\mcp\\locales\\zh.yaml", "offset": 75, "limit": 130}]

[tool: read_file · {"filePath": "d:\\repos\\CodeWiki-Plus\\codewiki\\mcp\\locales\\en.yaml", "offset": 72, "limit": 130}]
assistant: 差集确认中。注册表里 `team-memory-hook` 有 4 个参数（action、repo_path、mode、active_settle），zh.yaml/en.yaml 只写了 action、repo_path——`mode` 和 `active_settle` 缺失，运行时按设计返回 `[missing-i18n-key] prompts.team-memory-hook.args.mode` 哨兵，所以你看到的是 key。再看下 `init-wiki` 的 `active_settle` 和文件尾部几个 prompt 是否也缺。

[tool: read_file · {"filePath": "d:\\repos\\CodeWiki-Plus\\codewiki\\mcp\\locales\\zh.yaml", "offset": 218, "limit": 60}]

[tool: read_file · {"filePath": "d:\\repos\\CodeWiki-Plus\\codewiki\\mcp\\locales\\en.yaml", "offset": 201, "limit": 60}]
assistant: 差集确认完毕，共 3 个 key 在两份语料中都缺失（zh/en 各缺 3 个）：

| Prompt | 注册表参数 | 语料缺失 |
|---|---|---|
| `init-wiki` | repo_path, enable_task_management, **active_settle** | `active_settle` |
| `team-memory-hook` | action, repo_path, **mode**, **active_settle** | `mode`、`active_settle` |

根因：`_PROMPT_REGISTRY`（`codewiki/mcp/prompts.py:1634-1682`）后来加了 `mode`/`active_settle` 参数，但语料没同步；而守门测试 `test_i18n.py` 只校验 zh↔en **互相**覆盖（`test_en_covers_every_zh_key`），不校验「注册表 → 语料」方向，所以漏网。运行时按设计返回 `[missing-i18n-key] prompts.team-memory-hook.args.mode` 哨兵——这就是你看到的 key。

修复：补齐 4 处语料 + 加一条注册表覆盖守门测试。
assistant: 现在加守门测试：校验 `_PROMPT_REGISTRY` 的每个 prompt 的 title/description/args 在 zh/en 语料中都存在。
assistant: [tool: execute_command · cd /d d:\repos\CodeWiki-Plus && .venv\Scripts\python.exe -m pytest tests/test_i18n.py -q 2>&1 | tail -5]
assistant: 16 个测试全过（原 15 + 新增 1）。再快速验证运行时渲染不再出哨兵：

[tool: execute_command · d:\repos\CodeWiki-Plus\.venv\Scripts\python.exe -c "from codewiki.mcp import i18n; i18n.init_lang(); [print(lang, '|', i18n.t('prompts…
assistant: 修复完成，运行时渲染正常。写入工作记忆：

[tool: read_file · {"filePath": "d:\\repos\\CodeWiki-Plus\\.codebuddy\\memory\\2026-09-17.md"}]
assistant: 你说得对。已定位并修复：

## 根因

`_PROMPT_REGISTRY`（`codewiki/mcp/prompts.py:1668-1675`）后来给 `team-memory-hook` 加了 `mode`、`active_settle` 两个参数，给 `init-wiki` 加了 `active_settle`，但 `locales/zh.yaml` / `en.yaml` 没同步。运行时按设计返回 `[missing-i18n-key] prompts.team-memory-hook.args.mode` 哨兵——所以弹框里显示的是 key。

**守门测试为什么没拦住**：`test_i18n.py` 只校验 zh↔en **互相**覆盖（`test_en_covers_every_zh_key`），不校验「注册表 → 语料」方向。两份语料同时缺 key 时，测试依然全绿。

## 修复内容

1. **补齐语料**（zh + en 各 3 处）：
   - `prompts.init-wiki.args.active_settle`
   - `prompts.team-memory-hook.args.mode`
   - `prompts.team-memory-hook.args.active_settle`

2. **堵守门盲区**：`tests/test_i18n.py` 新增 `test_catalog_covers_every_registered_prompt`——遍历 `_PROMPT_REGISTRY` 每个 prompt 的 title/description/args，断言在 zh、en 两份语料中都能解析，缺任何一边都直接红。

## 验证

- `tests/test_i18n.py` **16 passed**（原 15 + 新增 1）
- 运行时实测 zh/en 两个语言的 `mode`/`active_settle` 均正常渲染中文/英文文案，不再出哨兵

注意：MCP server 是按进程启动时定语言的，需要重启 IDE 会话（或重连 MCP）才能看到修复后的文案。
user: <user_command>
--- commands: codewiki/启用/禁用任务管理（跨会话任务记忆）--- 
 管理 team-memory fusion 的对话自动采集 Hook。

**支持范围由 `codewiki/hooks.yaml` 注册表驱动**（家族归并：claude / cursor / codex / trae 四种 hook 格式）：
- **已验证支持**（日常使用背书）：`codebuddy`, `qoder`, `claude-code`, `trae`, `qwenwork`
- **理论支持**（家族归并推导，未经真机验证，接线后必须跑步骤 2A 第 5 步的模拟事件验证）：`cursor`, `codex-cli`, `gemini-cli`, `windsurf`, `kilocode`, `opencode`

用户请求：**启用**采集 Hook。执行步骤 1 确认现状后直接进入步骤 2A。

**主动沉淀叠加（active_settle=on）**：接线会向注入文件（默认 AGENTS.md）写入 CODEWIKI-ACTIVE-SETTLE 协议块——自然停顿点四判据（里程碑/关键决策/话题转向/收尾轮兜底）命中即直写沉淀（任务记忆 `add_task_memory` 无闸门 / 通用经验 `ingest_note(status="draft")` 保留确认闸门），收尾轮做带 `active_settle=true` 标记的保险采集；遗留的旧 CODEWIKI-QWENWORK 块会被一次性迁移为新块。采集断供宿主（trae / qwenwork）按注册表默认即为 on，无需显式指定；叠加关闭（`--active-settle off`）时接线会删除该块。

采集 Hook 只负责把对话捕获到 `repowiki/raw/`（仅采集、不蒸馏）；蒸馏是独立的显式步骤，见 distill-conversations prompt。

**当前项目探测结果**：`d:\repos\CodeWiki-Plus` 下检测到的智能体配置目录：`codebuddy`, `qoder`, `trae`。**只为探测到的智能体接线**——探测不凭空创建任何目录；用户想接未探测到的智能体时，由用户自行初始化该工具的配置目录后重跑本流程。

claude 家族（CodeBuddy/Qoder/Claude Code/Gemini CLI 及理论支持工具）接线格式一致（各自 `settings.json`，事件 SessionStart/SessionEnd），仅配置目录不同。cursor 家族（`hooks.json` + 事件名 sessionStart/stop）与 codex 家族（`hooks.json` 嵌套结构）格式不同，且 **cursor 家族采集降级**：stop 事件不携带 transcript_path，无正文可采（仅事件级诊断、不落盘）、无法完整蒸馏对话——为 cursor 家族接线前须向用户说明此限制。trae 家族（TRAE，`hooks.json` + 事件名 SessionStart/Stop/UserPromptSubmit，顶层 `{"version": 1, "hooks": {...}}`）已真机验证：SessionStart/UserPromptSubmit 完整可用，但 TRAE 无 SessionEnd 事件——Stop 每轮 Query 结束触发且不携带 transcript_path（仅 last_assistant_message），**采集同样降级（无正文可采，仅事件级诊断、不落盘）**，对话捕获依赖 AGENTS.md「会话收尾轮」norm 由 Agent 中介补漏——为 trae 家族接线前须向用户说明此限制。

## 步骤 1: 检查当前状态
依次检查项目根目录下**探测到的**每个智能体配置目录（如 `d:\repos\CodeWiki-Plus/.codebuddy/`、`d:\repos\CodeWiki-Plus/.qoder/`、`d:\repos\CodeWiki-Plus/.claude/` 等，以探测结果为准）：
- 每个目录下读取家族对应的配置文件（claude 家族 `settings.json`；cursor/codex/trae 家族 `hooks.json`）：**已启用** = 存在 SessionEnd 与 SessionStart（或家族对应事件名，trae 家族为 Stop）两个条目，且对应目录 `hooks/` 下 `capture_session_end.py` 与 `task_session_start.py` 两个脚本文件都物理存在（claude 家族 command 用项目相对路径如 `python ".qoder/hooks/task_session_start.py"`——宿主以项目根为工作目录执行命令；不写机器相关绝对路径、也不用 `$*_PROJECT_DIR` 变量（实测不可靠）；历史绝对路径条目可视为已启用，但建议重跑接线迁移为相对路径形式）
- 向用户报告哪些智能体已启用、哪些未启用

## 步骤 2A: 启用
**首选路径：运行 CLI 自动检测接线（推荐，覆盖全部已探测到的智能体）**

```powershell
codewiki install-hooks --repo-path d:\repos\CodeWiki-Plus --active-settle on
```

CLI 会自动检测项目根目录下存在哪些智能体配置目录（按 `codewiki/hooks.yaml` 注册表探测），检测到哪些就为哪些自动完成全部接线：
- 强制拷贝 hook 脚本与 `distill-worker.md` 到对应 `.codebuddy|.qoder|.claude|.gemini|.trae/hooks/` 与 `agents/`
- 幂等合并 `settings.json`（TRAE 为 `.trae/hooks.json`：顶层补 `version: 1`，SessionEnd 注册映射为 Stop 且不写 matcher）的 SessionStart/SessionEnd 注册（保留已有无关配置，重复运行不产生重复条目）
- 向 `AGENTS.md` upsert 任务记忆引导段（多 IDE 共享一份，只写一次）

CLI 不可用（`codewiki` 命令未安装）时，回退到下方手动步骤。手动接线时以 `.codebuddy` 为例，**Qoder / Claude Code / Gemini CLI 仅目标目录不同**：`.codebuddy/` ↔ `.qoder/` ↔ `.claude/` ↔ `.gemini/`（settings.json、hooks/、agents/ 的相对位置与内容完全一致，command 均为项目相对路径）。**仅为步骤 1 探测到的智能体执行手动接线；未探测到的智能体一律不接、不创建其目录**——本机安装了某工具不等于本仓库在用它，除非用户明确点名并确认。

### 手动兜底步骤
1. **确保两个 hook 脚本与 distill-worker subagent 就位（每次都强制覆盖拷贝）**。脚本必须物理存在于目标项目，IDE 不会自动创建它们。
   **不论目标是否已存在，每次启用都要从 CodeWiki 自带的源文件重新复制覆盖**，
   以保证与目标 `codewiki` 包版本一致（不要因为"已存在"就跳过，否则升级包后会残留旧脚本）：
   用以下命令解析 CodeWiki 自带的源文件路径，并**强制复制**到目标目录
   （务必复制，不要凭记忆重写，以免与 `codewiki` 包行为不一致）：

     ```powershell
     # 源文件随 codewiki 包发布：codewiki/hooks/ 下两个 hook 脚本 + codewiki/agents/distill-worker.md
     $pkg = python -c "import codewiki, os; print(os.path.dirname(codewiki.__file__).replace('\\','/'))"
     $destDir = Join-Path 'd:\repos\CodeWiki-Plus' '.codebuddy/hooks'
     $agentDir = Join-Path 'd:\repos\CodeWiki-Plus' '.codebuddy/agents'
     New-Item -ItemType Directory -Force -Path $destDir | Out-Null
     New-Item -ItemType Directory -Force -Path $agentDir | Out-Null
     Copy-Item (Join-Path $pkg 'hooks/capture_session_end.py') (Join-Path $destDir 'capture_session_end.py') -Force
     Copy-Item (Join-Path $pkg 'hooks/task_session_start.py') (Join-Path $destDir 'task_session_start.py') -Force
     Copy-Item (Join-Path $pkg 'agents/distill-worker.md') (Join-Path $agentDir 'distill-worker.md') -Force
     python -c "import ast; ast.parse(open(r'$destDir/capture_session_end.py', encoding='utf-8').read()); ast.parse(open(r'$destDir/task_session_start.py', encoding='utf-8').read()); assert open(r'$agentDir/distill-worker.md', encoding='utf-8').read().startswith('---'), 'distill-worker.md missing'; print('hook scripts + distill-worker.md copied OK')"
     ```

     若 `import codewiki` 失败（未 pip 安装且不在源码 checkout 内），回退：从
     `CODEWIKI_HOME` 环境变量指向的 checkout 取
     `$env:CODEWIKI_HOME/codewiki/hooks/` 下的两个脚本与
     `$env:CODEWIKI_HOME/codewiki/agents/distill-worker.md`，同样 Copy-Item 到 `$destDir` / `$agentDir`。
     兜底都不满足时，提示用户先 `pip install codewiki` 或设置 `CODEWIKI_HOME`，不要凭记忆写脚本。
     **为 Qoder/Claude Code 接线时，把上面 `$destDir` / `$agentDir` 中的 `.codebuddy` 换成 `.qoder` / `.claude` 即可。**
2. 创建或合并 `d:\repos\CodeWiki-Plus/.codebuddy/settings.json`，加入以下 hook 注册（保留文件中已有的无关配置；Qoder/Claude Code/Gemini CLI 写入 `.qoder/settings.json` / `.claude/settings.json` / `.gemini/settings.json`，command 中目录名随配置目录变化，其余完全一致）。**command 用项目相对路径（宿主以项目根为工作目录执行命令），不写机器相关绝对路径、也不用 `$*_PROJECT_DIR` 变量（各宿主变量展开经实测不可靠）**——settings.json 随仓库共享，绝对路径提交后队友克隆到其他目录即失效：

```json
{
  "hooks": {
    "SessionStart": [
      { "matcher": "startup", "hooks": [ { "type": "command", "command": "python \".codebuddy/hooks/task_session_start.py\"", "timeout": 15 } ] }
    ],
    "SessionEnd": [
      { "matcher": "other", "hooks": [ { "type": "command", "command": "python \".codebuddy/hooks/capture_session_end.py\"", "timeout": 30 } ] }
    ]
  }
}
```

   - `SessionStart`（matcher=`startup`）：新会话开始同步返回 `hookSpecificOutput.additionalContext`，把任务关联引导注入给 Agent，是"新建会话提示选任务"的确定性触发点；如需覆盖 `--resume` 恢复场景，matcher 改为 `startup|resume`。
   - `SessionEnd`：唯一可靠携带 `transcript_path` 的事件，能抓到完整正文。
   `PreCompact`/`Stop` 不带 transcript，无正文可采（hook 只输出 stderr 诊断、不落盘），故不注册。

2b. **TRAE（trae 家族）变体**：写入 `d:\repos\CodeWiki-Plus/.trae/hooks.json`（不是 settings.json），顶层多一个 `version` 字段，SessionEnd 换成 `Stop`（TRAE 无 SessionEnd 事件），且不写 matcher（TRAE 的 matcher 仅对 PreToolUse/PostToolUse/Notification 有效）：

```json
{
  "version": 1,
  "hooks": {
    "SessionStart": [
      { "hooks": [ { "type": "command", "command": "python \".trae/hooks/task_session_start.py\"", "timeout": 15 } ] }
    ],
    "Stop": [
      { "hooks": [ { "type": "command", "command": "python \".trae/hooks/capture_session_end.py\"", "timeout": 30 } ] }
    ],
    "UserPromptSubmit": [
      { "hooks": [ { "type": "command", "command": "python -m codewiki.mcp._ide_hook --enable", "timeout": 10 } ] }
    ]
  }
}
```

   注意 TRAE 的 Stop 每轮 Query 结束都触发（非会话级）且不携带 transcript_path——hook 采集无正文可采（仅 stderr 诊断、不落盘），对话捕获依赖 AGENTS.md「会话收尾轮」norm 由 Agent 中介采集补漏。接线前须向用户说明此降级。TRAE 环境变量注入 `TRAE_PROJECT_DIR` 与 `CLAUDE_PROJECT_DIR`，脚本已支持。

3. 向 `d:\repos\CodeWiki-Plus/AGENTS.md` 写入任务记忆会话引导段（启用采集后，新建会话时 Agent 才会提示用户关联/新建任务）。
   **只动标记块，绝不改 AGENTS.md 其余内容**：若已存在 `<!-- TEAM-MEMORY-TASK:START -->` 到 `<!-- TEAM-MEMORY-TASK:END -->` 之间的块，用下面文本整体替换；若不存在，追加到文件末尾（前面留一个空行）。以下文本按原样写入，含 START/END 注释标记：

<!-- TEAM-MEMORY-TASK:START -->
## Task memory (任务记忆)

跨会话延续长线工作上下文。任务记忆是**任务范围内的进度知识**（本次做了什么、下一步、待办），与 Wiki 笔记（**跨任务的通用经验**）互补。

**会话开始时（必须执行）：**
1. `list_tasks(status="active")` 列出进行中的任务
2. **必须用 `ask_followup_question` 弹框，且只弹一次、一框列全**：只调用 1 次，questions 数组只放 1 个 question（标题「任务关联」，multiSelect=false），options 一次性列出「每个进行中任务」+「新建任务…（在输入框直接输入名称）」+「跳过」。**严禁**因工具 schema 建议 2-4 个 options 就拆成多个 question 或分多次弹框；唯一例外是用户选了「新建任务…」却没给名字，可再弹一次要名字
3. 用 `set_session_task(source_session_id=<会话id>, task_id=<任务id>)` 绑定；列表里没有的任务名先 `create_task(title=<任务名>)` 再绑定；用户选「跳过」则本次不关联
4. `get_task_context(task_id=<选中任务>)` 拉取任务描述 + 记忆 + 关联笔记
5. `pending_raw_count > 0` 时**阻塞式补蒸馏，先记忆后回答**：发一个阻塞式 subagent 补蒸馏，**清空本任务的全部待蒸馏积压**（不设条数上限——只挑最近几条会让老积压永远轮不到），任务记忆与经验一次产出；完成后重新 `get_task_context` 拉取最新记忆再回答用户。subagent 失败/超时不重试——带旧记忆直接回答，未蒸馏的 raw 留在 raw/ 等下次会话再补。蒸馏产出的草稿笔记须 `confirm_note` 确认后才落盘；任务记忆直写、无需确认（ADR-0002）
6. **项目定向（按条件执行）**：若本会话上下文中**没有**已注入的 Team Doctrine / 知识库概览（hook 档宿主的 SessionStart 注入会带上；注入文件随项目上下文自动加载的宿主没有此注入），调用 `query_wiki(mode="overview")` 拉取一次；已注入则跳过，绝不重复拉取
7. **会话收尾（按条件执行）**：检查本文件是否存在 **CODEWIKI-ACTIVE-SETTLE 块**（HTML 注释标记包裹的独立小节，见下方条件）：
   - **存在**：按该块执行——自然停顿点命中四判据即直写沉淀（任务记忆 `add_task_memory` / 通用经验 `ingest_note(status="draft")`），收尾轮做带 `active_settle=true` 标记的保险采集；**跳过**下方传统收尾轮采集
   - **不存在**：按下方**传统收尾轮采集**执行

**传统收尾轮采集（任务完成 / 用户道别 / 用户显式要求记录时）：**
将本会话对话重建为 `[{role, content}]` 列表，调用 `capture_conversation(conversation=..., source_session_id=<本会话id>, task_id=<任务id>)` 落 raw。**user 消息必须逐字保留**（需求/纠正/决策是知识的主要来源），assistant 保留关键结论原句，工具调用略去。同一会话多次收尾采集会被 supersede 替换，不会堆积。

完整工作流、存储布局与实现约束见 MCP prompt：`get_prompt(name="task-workflow")` —— 按需获取，不在此重复。
<!-- TEAM-MEMORY-TASK:END -->

4. 前置条件：hook 启动的 python 进程必须能 import `codewiki` 包。满足任一即可：codewiki 已通过 pip 安装；hook 位于 CodeWiki 源码 checkout 内；或设置了 `CODEWIKI_HOME` 环境变量指向 checkout。都不满足时 wrapper 会跳过采集并输出带操作指引的 systemMessage（绝不阻塞 IDE）
5. 用模拟事件验证两个脚本（Qoder/Claude Code 用对应目录路径替换 `.codebuddy`；TRAE 的会话结束事件是 Stop，不带 transcript_path，见下方 TRAE 变体）：
   - SessionEnd（先准备一个小的 transcript 文件，如 `[{"role":"user","content":"测试"}]` 存为 d:/tmp/conv.json；期望 stdout 返回 `{"continue": true, "systemMessage": "team-memory capture started in background"}`）：wrapper 是 fire-and-forget，只回报「后台采集已启动」，**不回报采集结果**；是否真的落盘要等 1-2 秒后看 `d:\repos\CodeWiki-Plus/repowiki/raw/` 是否新增 `conv-*.md`（`source_session` = verify-1）。stdin 事件缺失或 JSON 非法时返回 `team-memory capture skipped: ...`，不会谎报成功。拼 `cwd` 时别写反斜杠路径（`d:
epos` 里的 `
`/`\C` 是非法 JSON 转义，事件会被整体丢弃）：

```powershell
'{"session_id":"verify-1","transcript_path":"d:/tmp/conv.json","cwd":"d:\repos\CodeWiki-Plus","hook_event_name":"SessionEnd","reason":"other"}' | python "d:\repos\CodeWiki-Plus/.codebuddy/hooks/capture_session_end.py"
```

   - SessionStart（期望 stdout 的 hookSpecificOutput.additionalContext 中包含"任务关联"）：

```powershell
'{"session_id":"verify-2","cwd":"d:\repos\CodeWiki-Plus","hook_event_name":"SessionStart","source":"startup"}' | python "d:\repos\CodeWiki-Plus/.codebuddy/hooks/task_session_start.py"
```

   - TRAE Stop（期望 stdout 的 systemMessage 正常返回、`repowiki/raw/` **不**新增任何文件——TRAE 无 SessionEnd/transcript_path，hook 无正文可采、不落盘，这是采集降级的预期行为；对话捕获由 Agent「会话收尾轮」norm 承担）：

```powershell
'{"session_id":"verify-3","hook_event_name":"Stop","stop_hook_active":false,"loop_count":0,"last_assistant_message":"done"}' | python "d:\repos\CodeWiki-Plus/.trae/hooks/capture_session_end.py"
```

6. 验证完成后删除测试产物：`d:\repos\CodeWiki-Plus/repowiki/raw/` 下 verify-1 会话生成的 conv-*.md 文件

## 步骤 2B: 关闭
**首选路径：运行 `codewiki install-hooks --repo-path d:\repos\CodeWiki-Plus --ide <name>` 可重新接线；关闭采集时**：
1. 依次检查探测到的各智能体目录（`.codebuddy/`、`.qoder/`、`.claude/`、`.gemini/` 等），从对应 `settings.json` 移除 SessionStart 与 SessionEnd 两个条目（其他 hook 保持不变；`"hooks": {}` 留空也可以）
2. 从 `d:\repos\CodeWiki-Plus/AGENTS.md` 移除任务记忆会话引导段：删除 `<!-- TEAM-MEMORY-TASK:START -->` 到 `<!-- TEAM-MEMORY-TASK:END -->` 之间的整段（含两行注释标记本身）；若不存在该标记块则无需处理，其余内容保持不动
3. **同步移除主动沉淀协议块**：从 `d:\repos\CodeWiki-Plus/AGENTS.md` 删除 `<!-- CODEWIKI-ACTIVE-SETTLE:START -->` 到 `<!-- CODEWIKI-ACTIVE-SETTLE:END -->` 之间的整段（含两行注释标记本身）；遗留的旧 `<!-- CODEWIKI-QWENWORK:START -->` 到 `<!-- CODEWIKI-QWENWORK:END -->` 块（若存在）一并删除。不存在的标记块无需处理，块外内容保持不动
4. 已采集的 raw 文件保留在 `repowiki/raw/`，之后仍可蒸馏；关闭采集不会删除它们
5. hook 脚本 `capture_session_end.py`、`task_session_start.py` 与 subagent 定义 `distill-worker.md` 可保留也可删除；重新启用时步骤 2A 会自动补回

## 注意事项
- Hook 接线支持范围见开头注册表清单（已验证：CodeBuddy/Qoder/Claude Code；理论支持按家族归并列出，接线后必须模拟事件验证）。完全不支持 hook 的运行时请改用 `capture_conversation` MCP 工具手动采集
- 仅在会话结束时（SessionEnd）采集一次，落到 repowiki/raw/conv-*.md；会话级 supersede 去重保证每个会话只保留最新一份完整 transcript，不会膨胀
- Hook 永不蒸馏、永不写 wiki 页面、永不使 IDE 失败（异常仅输出到 stderr，退出码保持 0）--- commands end ---
 
</user_command>

@command://codewiki/启用/禁用任务管理（跨会话任务记忆）
assistant: 执行步骤 1：检查三个已探测智能体目录的接线现状。

[tool: read_file · {"filePath": "d:\\repos\\CodeWiki-Plus\\.codebuddy\\settings.json"}]

[tool: read_file · {"filePath": "d:\\repos\\CodeWiki-Plus\\.qoder\\settings.json"}]

[tool: read_file · {"filePath": "d:\\repos\\CodeWiki-Plus\\.trae\\hooks.json"}]

[tool: list_dir · {"target_directory": "d:\\repos\\CodeWiki-Plus\\.codebuddy\\hooks"}]

[tool: list_dir · {"target_directory": "d:\\repos\\CodeWiki-Plus\\.qoder\\hooks"}]

[tool: list_dir · {"target_directory": "d:\\repos\\CodeWiki-Plus\\.trae\\hooks"}]
assistant: 三个智能体均已接线（配置条目齐全、脚本物理存在、command 为项目相对路径）。按步骤 2A 首选路径运行 CLI 重新接线（本次带 `--active-settle on`）：

[tool: execute_command · d:\repos\CodeWiki-Plus\.venv\Scripts\python.exe -m codewiki.cli install-hooks --repo-path d:\repos\CodeWiki-Plus --active-settle on]
assistant: [tool: execute_command · d:\repos\CodeWiki-Plus\.venv\Scripts\codewiki.exe install-hooks --repo-path d:\repos\CodeWiki-Plus --active-settle on]
assistant: CLI 接线完成。验证 AGENTS.md 的 active-settle 协议块是否写入，并跑模拟事件验证：

[tool: search_content · d:\repos\CodeWiki-Plus\AGENTS.md]
assistant: [tool: read_file · {"filePath": "d:\\repos\\CodeWiki-Plus\\AGENTS.md", "offset": 155, "limit": 50}]
assistant: AGENTS.md 两个标记块都已就位。跑模拟事件验证三个脚本：

[tool: execute_command · Set-Content -Path 'd:/tmp/conv.json' -Value '[{"role":"user","content":"测试"}]' -Encoding UTF8; '{"session_id":"verify-1","transcript_p…
assistant: [tool: execute_command · Start-Sleep -Seconds 2; Get-ChildItem 'd:\repos\CodeWiki-Plus\repowiki\raw\' -Filter 'conv-*.md' | Where-Object { (Get-Content $_.Full…

[tool: execute_command · '{"session_id":"verify-2","cwd":"d:/repos/CodeWiki-Plus","hook_event_name":"SessionStart","source":"startup"}' | python "d:\repos\Code…
assistant: SessionStart 验证通过（additionalContext 含「任务关联」）。检查 verify-1 落盘情况（换用带编码的方式）：

[tool: execute_command · Start-Sleep -Seconds 2; Get-ChildItem 'd:\repos\CodeWiki-Plus\repowiki\raw\' -Filter 'conv-*.md' | Sort-Object LastWriteTime -Descendi…
assistant: `conv-测试.md`（19:37:28，即 verify-1 会话产物）已落盘。验证 TRAE Stop 事件（预期不落盘）：

[tool: execute_command · '{"session_id":"verify-3","hook_event_name":"Stop","stop_hook_active":false,"loop_count":0,"last_assistant_message":"done"}' | python …
assistant: [tool: execute_command · Start-Sleep -Seconds 2; (Get-ChildItem 'd:\repos\CodeWiki-Plus\repowiki\raw\' -Filter 'conv-*.md' | Where-Object { $_.LastWriteTime -g…
assistant: TRAE Stop 未落盘（符合降级预期）。清理测试产物：

[tool: delete_file · {"target_file": "d:\\repos\\CodeWiki-Plus\\repowiki\\raw\\conv-测试.md", "explanation": "删除 verify-1 会话生成的测试产物"}]
assistant: ## 接线完成报告

**步骤 1 现状**：三个已探测智能体（`codebuddy` / `qoder` / `trae``）此前均已启用——配置条目齐全、hook 脚本物理存在、command 均为项目相对路径。

**步骤 2A 执行**（CLI 首选路径，`--active-settle on`）：

| 智能体 | 脚本拷贝 | 配置 | AGENTS.md |
|---|---|---|---|
| codebuddy | 3 文件强制覆盖 | 已接线，无变更 | 任务记忆段更新 |
| qoder | 3 文件强制覆盖 | 已接线，无变更 | 已存在，无变更 |
| trae | 3 文件强制覆盖 | 已接线，无变更 | 已存在，无变更 |

**主动沉淀叠加**：`CODEWIKI-ACTIVE-SETTLE` 协议块已写入 `AGENTS.md:181-200`（自然停顿点四判据直写沉淀 + 收尾轮保险采集）。

**模拟事件验证**（全部通过）：
- SessionEnd（verify-1）：返回 `team-memory capture started in background`，2 秒后 `repowiki/raw/` 落盘 `conv-测试.md` ✓
- SessionStart（verify-2）：`additionalContext` 包含「任务关联」引导 ✓
- TRAE Stop（verify-3）：正常返回、**不落盘**——TRAE 无 SessionEnd/transcript_path，采集降级为仅诊断，对话捕获由「会话收尾轮」norm 承担（预期行为）✓

测试产物已清理。注意：本次接线对 settings.json 无实际变更，但 hook 脚本已刷新为最新包版本；新会话生效。
