---
type: Conversation
title: "conversation 20260917T112335Z"
status: distilled
stale_after: 2026-12-16
generated: { by: codewiki/5.10.1, at: 2026-09-17T11:23:35Z }
captured_at: "2026-09-17T11:23:35Z"
content_hash: "sha256:18dbe6e86ba917ccd51a5f914a67fe6d0699d16a3d2145230783929ccc965d7b"
friction_score: 5
friction_signals: "correction=0,interrupt=0,repeat=0,user_turns=5"
keep_raw: false
link_to: ""
source_session: "83eb83aa8dd044e79005b05e730d55dc"
task_id: "OpenWiki-竞品调研"
turn_count: 47
---

# Conversation Transcript

user: <working_memory_content>
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

https://github.com/mem0ai/mem0  调研这个项目的实现机制，以及分析值得CodeWiki借鉴的
assistant: [tool: ask_followup_question · {"questions": "[{\"header\": \"任务关联\", \"multiSelect\": false, \"options\": [{\"description\": \"task_id=CodeWiki-架构深化分析\", \"la…
user: <question>本次会话要关联哪个任务？（若列表里没有想要的，可直接在输入框输入新任务名后回车）</question>
<answers>
OpenWiki 竞品调研
</answers>
</question_item>
</questions>
</question_answer>
assistant: [tool: mcp_get_tool_description · {"toolRequests": "[[\"codewiki\",\"set_session_task\"],[\"codewiki\",\"get_task_context\"]]"}]
assistant: [tool: mcp_call_tool · {"serverName": "codewiki", "toolName": "set_session_task", "arguments": "{\"source_session_id\": \"83eb83aa8dd044e79005b05e730d55dc\", \…
assistant: [tool: mcp_call_tool · {"serverName": "codewiki", "toolName": "get_task_context", "arguments": "{\"task_id\": \"OpenWiki-竞品调研\"}"}]
assistant: 任务已关联「OpenWiki 竞品调研」，无待蒸馏积压。现在开始调研 mem0 项目。

[tool: use_skill · research]
assistant: 我先克隆 mem0 仓库作为一手资料，同时看看仓库里已有的竞品调研报告的存放惯例。

[tool: execute_command · git clone --depth 1 https://github.com/mem0ai/mem0.git "%TEMP%\mem0-research" 2>&1 | Select-Object -Last 3]

[tool: search_file · *openwiki*]

[tool: search_file · *竞品*]
assistant: [tool: execute_command · git clone --depth 1 https://github.com/mem0ai/mem0.git "%TEMP%\mem0-research" && echo CLONE_OK]

[tool: read_file · {"filePath": "d:\\repos\\CodeWiki-Plus\\docs\\compare\\openwiki-notes.md", "limit": 80}]
assistant: 克隆成功。现在并行读取 mem0 的核心文件。

[tool: list_dir · {"target_directory": "C:\\Users\\ADMINI~1\\AppData\\Local\\Temp\\mem0-research"}]

[tool: read_file · {"filePath": "C:\\Users\\ADMINI~1\\AppData\\Local\\Temp\\mem0-research\\README.md", "limit": 150}]
assistant: [tool: list_dir · {"target_directory": "C:\\Users\\ADMINI~1\\AppData\\Local\\Temp\\mem0-research\\mem0"}]

[tool: list_dir · {"target_directory": "C:\\Users\\ADMINI~1\\AppData\\Local\\Temp\\mem0-research\\mem0\\memory"}]
assistant: [tool: read_file · {"filePath": "C:\\Users\\ADMINI~1\\AppData\\Local\\Temp\\mem0-research\\mem0\\memory\\main.py"}]
assistant: [tool: read_file · {"filePath": "C:\\Users\\ADMINI~1\\AppData\\Local\\Temp\\mem0-research\\mem0\\memory\\main.py", "limit": 250}]

[tool: search_content · C:\Users\ADMINI~1\AppData\Local\Temp\mem0-research\mem0\memory\main.py]
assistant: [tool: read_file · {"filePath": "C:\\Users\\ADMINI~1\\AppData\\Local\\Temp\\mem0-research\\mem0\\memory\\main.py", "offset": 760, "limit": 450}]
assistant: [tool: read_file · {"filePath": "C:\\Users\\ADMINI~1\\AppData\\Local\\Temp\\mem0-research\\mem0\\memory\\main.py", "offset": 1379, "limit": 420}]
assistant: [tool: read_file · {"filePath": "C:\\Users\\ADMINI~1\\AppData\\Local\\Temp\\mem0-research\\mem0\\configs\\prompts.py", "limit": 200}]

[tool: read_file · {"filePath": "C:\\Users\\ADMINI~1\\AppData\\Local\\Temp\\mem0-research\\mem0\\utils\\scoring.py", "limit": 150}]
assistant: [tool: search_content · C:\Users\ADMINI~1\AppData\Local\Temp\mem0-research\mem0\configs\prompts.py]

[tool: read_file · {"filePath": "C:\\Users\\ADMINI~1\\AppData\\Local\\Temp\\mem0-research\\mem0\\memory\\storage.py", "limit": 120}]
assistant: -

[tool: list_dir · {"target_directory": "C:\\Users\\ADMINI~1\\AppData\\Local\\Temp\\mem0-research\\mem0\\utils"}]

[tool: read_file · {"filePath": "C:\\Users\\ADMINI~1\\AppData\\Local\\Temp\\mem0-research\\mem0\\utils\\entity_extraction.py", "limit": 100}]
assistant: -

[tool: read_file · {"filePath": "C:\\Users\\ADMINI~1\\AppData\\Local\\Temp\\mem0-research\\mem0\\memory\\main.py", "offset": 488, "limit": 280}]
assistant: -

[tool: list_dir · {"target_directory": "C:\\Users\\ADMINI~1\\AppData\\Local\\Temp\\mem0-research\\mem0\\vector_stores"}]

[tool: read_file · {"filePath": "C:\\Users\\ADMINI~1\\AppData\\Local\\Temp\\mem0-research\\mem0\\memory\\main.py", "offset": 1815, "limit": 200}]
assistant: [tool: read_file · {"filePath": "C:\\Users\\ADMINI~1\\AppData\\Local\\Temp\\mem0-research\\mem0\\memory\\main.py", "offset": 2014, "limit": 180}]

[tool: read_file · {"filePath": "C:\\Users\\ADMINI~1\\AppData\\Local\\Temp\\mem0-research\\mem0\\memory\\main.py", "offset": 1208, "limit": 170}]
assistant: 核心管线已清楚。再看几个外围模块：proxy（OpenAI 兼容层）、skills（Agent 技能）、notices（提示系统）和 CLI。

[tool: list_dir · {"target_directory": "C:\\Users\\ADMINI~1\\AppData\\Local\\Temp\\mem0-research\\mem0\\proxy"}]

[tool: list_dir · {"target_directory": "C:\\Users\\ADMINI~1\\AppData\\Local\\Temp\\mem0-research\\skills"}]

[tool: read_file · {"filePath": "C:\\Users\\ADMINI~1\\AppData\\Local\\Temp\\mem0-research\\mem0\\memory\\notices.py", "limit": 120}]
assistant: [tool: read_file · {"filePath": "C:\\Users\\ADMINI~1\\AppData\\Local\\Temp\\mem0-research\\mem0\\proxy\\main.py", "limit": 180}]

[tool: read_file · {"filePath": "C:\\Users\\ADMINI~1\\AppData\\Local\\Temp\\mem0-research\\skills\\mem0\\SKILL.md", "limit": 120}]
assistant: 再看检索（混合搜索）与图记忆的实现要点。

[tool: search_content · C:\Users\ADMINI~1\AppData\Local\Temp\mem0-research\mem0\memory\main.py]

[tool: list_dir · {"target_directory": "C:\\Users\\ADMINI~1\\AppData\\Local\\Temp\\mem0-research\\mem0\\memory\\graph_memory"}]
assistant: [tool: search_content · C:\Users\ADMINI~1\AppData\Local\Temp\mem0-research\mem0\memory\main.py]

[tool: search_content · C:\Users\ADMINI~1\AppData\Local\Temp\mem0-research\mem0\memory\main.py]
assistant: [tool: search_content · C:\Users\ADMINI~1\AppData\Local\Temp\mem0-research\mem0\utils\scoring.py]

[tool: list_dir · {"target_directory": "C:\\Users\\ADMINI~1\\AppData\\Local\\Temp\\mem0-research\\mem0\\graphs"}]
assistant: [tool: list_dir · {"target_directory": "C:\\Users\\ADMINI~1\\AppData\\Local\\Temp\\mem0-research\\mem0"}]

[tool: search_content · C:\Users\ADMINI~1\AppData\Local\Temp\mem0-research\mem0\memory\main.py]
assistant: 再确认 add() 的 infer 推断管线关键步骤，以便准确引用。

[tool: read_file · {"filePath": "C:\\Users\\ADMINI~1\\AppData\\Local\\Temp\\mem0-research\\mem0\\memory\\main.py", "offset": 905, "limit": 180}]
assistant: [tool: search_content · C:\Users\ADMINI~1\AppData\Local\Temp\mem0-research]

[tool: search_content · C:\Users\ADMINI~1\AppData\Local\Temp\mem0-research\mem0\memory\main.py]
assistant: 核心机制已经摸清。看一下已有竞品调研文档的格式惯例，然后写报告。

[tool: list_dir · {"target_directory": "d:\\repos\\CodeWiki-Plus\\docs\\compare"}]

[tool: read_file · {"filePath": "d:\\repos\\CodeWiki-Plus\\docs\\compare\\openwiki-notes.md", "limit": 60}]
assistant: [tool: read_file · {"filePath": "d:\\repos\\CodeWiki-Plus\\docs\\compare\\openwiki-notes.md", "offset": 60}]
assistant: 格式惯例已明确。现在写 mem0 调研报告。

[tool: write_to_file · {"filePath": "d:\\repos\\CodeWiki-Plus\\docs\\compare\\mem0-notes.md", "content": "# mem0（mem0ai/mem0）调研笔记\n\n> 调研对象：本地克隆 `%TEMP%\\mem0-…
assistant: [tool: write_to_file · {"filePath": "d:\\repos\\CodeWiki-Plus\\.codebuddy\\memory\\2026-09-17.md", "content": "# 2026-09-17\n\n## mem0 竞品调研（OpenWiki 竞品调研任务）\n-…
assistant: 调研完成，报告已落盘 `docs/compare/mem0-notes.md`（遵循 openwiki-notes.md 的格式惯例，全部论断标注源码行号）。核心结论：

## mem0 实现机制（源码核对）

**架构**：OSS Python SDK + TS SDK + 托管平台三位一体；可插拔工厂（28 个向量库 / 15 个 embedder / 21 个 LLM）+ SQLite 辅助存储（history 账本 + 原始消息）。

**add() 写入管线**（`mem0/memory/main.py:916-1084`）——V3 分阶段批处理：
1. 取最近 10 条历史消息做上下文
2. 向量检索 top 10 相似记忆，**UUID 映射成整数 "0","1","2"** 再喂给 LLM——模型无法幻觉出不存在的记忆 ID（`main.py:933-938`）
3. **单次 LLM 调用**输出 `ADD/UPDATE/DELETE/NONE` 事件流，一次完成提取+判重+冲突消解
4. MD5 哈希确定性去重（批内 + 对检索结果），零 LLM 成本
5. 批量落库（带逐条降级）+ 实体链接（non-fatal）

**search() 检索**（`main.py:1628-1668`、`utils/scoring.py:60-119`）：语义（4 倍过采样）+ BM25（写入时预计算 lemmatized 副本）+ 实体 boost（≤0.5）三信号加性融合，**语义分先过 threshold 门槛**——关键词只能提排序，救不回语义不及格的候选。

**重要信号**：2025 年 mem0 删掉了全部图数据库驱动（Neo4j/Memgraph/Kuzu 等，约 4000 行，PR #4805），改为轻量实体链接 + 检索期 boost——验证了 CodeWiki `ontology.yaml` 路线，不必引入图库。

## 值得 CodeWiki 借鉴（按性价比排序）

| 借鉴点 | 落点 | 成本/收益 |
|---|---|---|
| 整数 ID 反幻觉映射 | `distill_conversation`/`consolidate_notes` 的 UPDATE/MERGE 路径 | 低/高 |
| 单次调用输出事件流 | 蒸馏 submit 协议加 `event` 字段，蒸馏期一次完成覆盖 | 低/高 |
| MD5 哈希前置去重 | `ingest_note` 入库前查哈希 | 极低/中 |
| 混合打分 + explain | `query_wiki` 加 BM25 信号与门槛门控 | 中/高 |
| 变更历史账本 | 笔记存储层加 SQLite history 表 | 中/中 |
| Skill 分发渠道 | MCP prompts 包装成 SKILL.md 随包分发 | 低/中 |

**明确不借鉴**：mem0 的自动 UPDATE/DELETE 无确认闸门（一次 LLM 调用直接改删存量记忆，靠 history 账本兜底）——它赌事实低价值，CodeWiki 的知识是决策依据，draft→confirm 闸门必须保留。

**一句话**：mem0 的工程智慧是“用确定性簿记包裹 LLM 不确定性”，每一层都在收窄 LLM 自由度——这与 CodeWiki 的 Team Doctrine（工具做簿记、推理在调用方）高度同构，机制可直接吸收。
user: mem0也会抓取聊天记录吗
assistant: 会。mem0 在 `add()` 管线里**始终把原始对话消息落库**，这与 CodeWiki 的 `capture_conversation` → `repowiki/raw/` 暂存区是同构设计：

1. **无条件保存**：即使 LLM 一条事实都没提取出来，也会先 `db.save_messages(messages, session_scope)` 存原始消息再返回空（`mem0/memory/main.py:986-989`，注释明确 "Save messages even if nothing extracted"）；正常路径在 Phase 8 落库（`main.py:1192-1193`）。
2. **存哪**：SQLite 的 messages 表（`mem0/memory/storage.py:18` `_create_messages_table`），按 session scope（user_id/agent_id/run_id 组合）隔离。
3. **用途**：下次 `add()` 时取该 scope 最近 10 条历史消息（`main.py:920` `get_last_messages`）喂给提取 prompt，用于消解新消息里的代词和指代（`configs/prompts.py:519-521` "Last k Messages ... resolve references and pronouns"）——即原始记录不是归档用，是**下一轮提取的上下文**。
4. **代理层自动抓**：`mem0/proxy/main.py:100-105` 拦截 OpenAI 兼容的 `chat.completions.create`，只要最后一条是 user 消息，就后台 daemon 线程自动 `add()` 整段对话——应用零改造，聊天记录被静默采集。

两点差异值得注意：

- **mem0 的 raw 永不删除**（没有 CodeWiki 那种“蒸馏完成后删 raw”的机制），因为历史消息是提取管线的常驻输入，不是待蒸馏暂存区；
- **mem0 抓取是静默的**（proxy 层自动触发），CodeWiki 的采集 hook 默认关、蒸馏永不自动——这是确认闸门哲学的差异在采集端的延伸。
user: mem0是如何抓取的？没有使用Hook吗
assistant: [tool: search_content · C:\Users\ADMINI~1\AppData\Local\Temp\mem0-research]
assistant: [tool: search_content · C:\Users\ADMINI~1\AppData\Local\Temp\mem0-research\integrations]

[tool: list_dir · {"target_directory": "C:\\Users\\ADMINI~1\\AppData\\Local\\Temp\\mem0-research\\integrations"}]
assistant: [tool: list_dir · {"target_directory": "C:\\Users\\ADMINI~1\\AppData\\Local\\Temp\\mem0-research\\integrations\\agent-plugin-core"}]

[tool: search_content · C:\Users\ADMINI~1\AppData\Local\Temp\mem0-research\integrations\agent-plugin-core]
assistant: [tool: read_file · {"filePath": "C:\\Users\\ADMINI~1\\AppData\\Local\\Temp\\mem0-research\\integrations\\agent-plugin-core\\python\\hook_runner.py", "limit": 2…
assistant: [tool: read_file · {"filePath": "C:\\Users\\ADMINI~1\\AppData\\Local\\Temp\\mem0-research\\integrations\\agent-plugin-core\\python\\hook_runner.py", "offset": …
assistant: 是的，mem0 大量使用 Hook——我上一轮只讲了 SDK/proxy 层，漏了 `integrations/` 下的 Agent 插件体系，这里补全。它有**三层抓取机制**，Hook 是其中最重要的一层：

## 1. SDK 显式调用（应用层）

应用代码自己调 `m.add(messages, user_id=...)`，对话由应用主动喂进来。

## 2. OpenAI 兼容代理（框架层）

`mem0/proxy/main.py:100-105` 拦截 `chat.completions.create`，后台 daemon 线程自动 `add()`——无 Hook，靠 monkey-patch。

## 3. Agent 宿主 Hook 插件（IDE/Agent 层，最完整）

`integrations/` 下有 **15 个宿主插件**（claude-code、cursor、codex、opencode、kimi、antigravity、deepseek、pi-agent、openclaw 等），共享一个 `agent-plugin-core` 内核。以 Cursor 为例，`hooks/hooks.json` 注册了 **8 个生命周期事件**（`integrations/cursor-plugin/hooks/hooks.json:4-11`）：

| Hook 事件 | 干什么 |
|---|---|
| `sessionStart` | 恢复 pending handoff、记录会话开始 |
| `beforeSubmitPrompt` | **首个 prompt 时搜索记忆并注入上下文**（`hook_runner.py:62-94`，通过 `hookSpecificOutput.additionalContext` 注入，top_k=5、超时 2s、prompt <20 字符不搜） |
| `postToolUse` / `postToolUseFailure` | 记录工具调用 |
| `stop` / `afterAgentResponse` | 记录 assistant 回复（`default_record_stop`，`hook_runner.py:52-59`） |
| `preCompact` / `sessionEnd` | 触发 flush |

**关键工程设计**（`integrations/agent-plugin-core/python/hook_runner.py`）：

- **Hook 进程只做轻量记录，重活全部 handoff 给独立 flush worker**：hook 把 payload 写成 `pending/*.json` 文件，再 `subprocess.Popen` 拉起 detached 的 `flush_worker.py` 异步上传（`_launch_handoff`，`hook_runner.py:97-128`）——hook 本身毫秒级返回，不阻塞宿主 Agent；
- **崩溃恢复**：`.running` 文件超过 300 秒视为 stale，改回 `.json` 重新排队；pending 包 7 天过期；每次 session-start 最多恢复 5 个（`recover_pending_handoffs`，`hook_runner.py:131-155`）；
- **三种 flush 触发**：session-end（默认）、periodic checkpoint、idle（默认 300 秒无活动）；
- **fail-open**：JSON 解析失败返回 `{}`、异常只写 `plugin-errors.log`、`entry_point` 永不非零退出（`hook_runner.py:352-359`）——与 CodeWiki 的 Doctrine 完全同构；
- **可暂停**：`pause` skill 一条命令停采集，pending 包保留不丢（`cursor-plugin/skills/pause/SKILL.md`）。

## 与 CodeWiki 的对照

CodeWiki 的 `capture_session_end.py` / `task_session_start.py` hook 只在**会话收尾**落一次 raw；mem0 是**全生命周期事件流**（prompt→tool→response→compact→end），且 hook 与上传解耦（本地 evidence store → detached worker 异步 flush）。值得借鉴的增量点：

1. **首 prompt 记忆注入**：CodeWiki 目前靠 system_reminder 注入 Doctrine，mem0 的“第一条 user prompt 触发检索、`additionalContext` 注入”模式可让 `query_wiki` 结果按需进入上下文，而非全量预载；
2. **hook/worker 解耦 + pending 恢复**：CodeWiki 的 hook 直接写文件已足够轻，但如果未来 hook 要做网络调用（如上传到平台版），mem0 的 handoff 文件 + stale 恢复 + 数量上限是现成的可靠性模板；
3. **idle/periodic flush**：长会话不等收尾，中途 checkpoint——对应 CodeWiki 长会话的 raw 积压问题（当前只能等 session-end 采集）。
user: 你觉得他的这种hook机制值得我们借鉴吗
assistant: 先快速核对一下 CodeWiki 自己的 hook 现状，再下判断。

[tool: read_file · {"filePath": "d:\\repos\\CodeWiki-Plus\\codewiki\\hooks\\capture_session_end.py", "limit": 80}]

[tool: read_file · {"filePath": "d:\\repos\\CodeWiki-Plus\\codewiki\\hooks\\task_session_start.py", "limit": 60}]
assistant: 值得**选择性**借鉴，但不是照搬——核对完 CodeWiki 自己的 hook 实现后，我的判断是：**架构哲学两者已经同构，mem0 真正的增量在三个具体机制上，其中只有一个对 CodeWiki 是真痛点**。

## 已经对齐的部分（不用学）

mem0 hook 机制的核心原则，CodeWiki 现有实现（`codewiki/hooks/capture_session_end.py`）已经全部做到：

| mem0 的做法 | CodeWiki 现状 |
|---|---|
| hook 轻量、重活外移 | SessionEnd hook 已是 detached 后台进程，毫秒级返回（`capture_session_end.py:45-51`） |
| fail-open 永不阻塞宿主 | 同样如此，且“成功只代表启动了采集”的语义比 mem0 说得更清楚（`capture_session_end.py:53-59`） |
| 采集与蒸馏分离 | CodeWiki 更彻底：hook 只落 raw，蒸馏永不自动 |

## 三个增量机制的真实价值评估

**1. pending handoff 崩溃恢复（`hook_runner.py:131-155`）——低价值**
mem0 需要它是因为 flush 要**上传云端 API**（网络调用不可靠）。CodeWiki 的 capture 是本地写文件，失败面小得多。除非未来 hook 引入网络环节，否则这是为不存在的问题买保险。

**2. 首 prompt 检索注入（`beforeSubmitPrompt` → `additionalContext`）——思想可取，落地受限**
mem0 的 hook 能做检索注入，是因为它只需调一次 embedding API（纯向量检索，2s 超时）。CodeWiki 的 `query_wiki` 检索质量依赖关键词/语义判断，hook 是无 LLM 的确定性脚本，做不了“从 user prompt 推导检索词”。而且 CodeWiki 已有 SessionStart 注入 Doctrine + 任务提示的硬触发通道（`task_session_start.py:16-27`），任务记忆靠 `get_task_context` 在绑定后拉取——链路是完整的。**真正可借鉴的只是“按需注入”思想**：如果未来 query_wiki 支持纯向量检索，可以在首 prompt 时注入 top-3 相关笔记标题（只给标题不给正文，控制成本）。

**3. idle/periodic checkpoint——真痛点，但已踩过坑**
这是 mem0 机制里 CodeWiki 唯一的真实痛点对应物：**长会话中途 IDE 崩溃/强杀，SessionEnd 不触发，整段对话丢失**。mem0 用 `stop`/`preCompact` 事件做中途 checkpoint 解决了这个问题。但 CodeWiki 已经试过这条路并主动回撤——CodeBuddy 的 Stop/PreCompact 事件**不携带 transcript_path**，只能产出重复的 no-op 信封，2026-09-16 已清理（依据：`capture_session_start.py:14-18` 的注释和知识库笔记 `2026-09-16-移除事件信封落盘无-transcript-的-hook-生命周期事件一律-no-op`）。这是**宿主能力限制，不是设计缺陷**——除非 CodeBuddy 未来给 Stop 事件补上 transcript 增量，否则此路不通。

## 结论

**不建议为 mem0 的 hook 机制做架构改动。** 两者在“轻量 hook + 重活外移 + fail-open”上已经殊途同归，mem0 剩下的机制要么解决的是 CodeWiki 没有的问题（云端上传恢复），要么被宿主能力卡死（无 transcript 的中途 checkpoint）。符合 Doctrine 的判断：成本可见性优先于新造能力——当前 hook 链路的真实瓶颈是“长会话崩溃丢对话”，而它的解法在 IDE 侧而非 CodeWiki 侧。

唯一值得留个记号的：如果 CodeBuddy 将来给 Stop/PreCompact 补上 transcript 增量，mem0 的 periodic checkpoint 模式（`checkpoint_due` 按条数阈值触发）是现成的实现模板。

我把 hook 机制这节补进调研报告：
assistant: 报告已更新（`docs/compare/mem0-notes.md` 新增第 7 节「Agent 宿主 Hook 插件体系」及借鉴评估）。

总结我的判断：**mem0 的 hook 机制不值得 CodeWiki 做架构级借鉴**——两者在核心哲学（轻量 hook、重活外移、fail-open、采集与蒸馏分离）上已经同构，mem0 的三个增量机制中，pending 恢复是为云端上传买保险（CodeWiki 本地写文件无此需求），首 prompt 注入依赖无 LLM 的向量检索（CodeWiki hook 做不了检索词推导），periodic checkpoint 对应的真痛点（长会话崩溃丢对话）则被 CodeBuddy Stop/PreCompact 事件不携带 transcript 的宿主限制卡死——这条路 CodeWiki 已经试过并在 2026-09-16 主动回撤。留一个观察点即可：若 IDE 将来给中途事件补上 transcript 增量，mem0 的 `checkpoint_due` 阈值模式是现成的实现模板。
