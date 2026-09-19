---
type: Conversation
title: "conversation 20260919T111617Z"
status: distilled
stale_after: 2026-12-18
generated: { by: codewiki/5.10.1, at: 2026-09-19T11:16:17Z }
captured_at: "2026-09-19T11:16:17Z"
content_hash: "sha256:1c7d773293dc0437bbe8200785934c8c56111c46a4d3979a6d5b1043e1263660"
friction_score: 5
friction_signals: "correction=0,interrupt=0,repeat=0,user_turns=5"
keep_raw: false
link_to: ""
source_session: "d30d6164edba4f13ada8ca7a51b8ac13"
task_id: "他山之石"
turn_count: 77
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

https://github.com/usememos/memos.git 调研这个项目
assistant: [tool: ask_followup_question · {"questions": "[{\"header\": \"任务关联\", \"multiSelect\": false, \"options\": [{\"description\": \"task_id=产品维护\", \"label\": \"产品…
user: <question>本次会话要关联哪个任务？（调研 memos 项目——若列表里没有想要的任务，可直接在弹框的输入框里输入新任务名后回车）</question>
<answers>
他山之石
</answers>
</question_item>
</questions>
</question_answer>
assistant: [tool: mcp_call_tool · {"serverName": "codewiki", "toolName": "set_session_task", "arguments": "{\"source_session_id\": \"d30d6164edba4f13ada8ca7a51b8ac13\", \…

[tool: mcp_call_tool · {"serverName": "codewiki", "toolName": "get_task_context", "arguments": "{\"task_id\": \"他山之石\"}"}]
assistant: 任务已绑定「他山之石」，无蒸馏积压。开始调研 memos 项目——按本任务 SOP：克隆到 `D:\repos`、读代码而非文档站、结论带文件:行号、逐项在本仓证伪、出处置表、存档 `docs/`。

[tool: execute_command · if (Test-Path D:\repos\memos) { git -C D:\repos\memos fetch origin 2>&1 | Out-Null; git -C D:\repos\memos log -1 --format='%H %ci %s' …
assistant: [tool: execute_command · git -C D:\repos\memos log -1 --format='%H %ci %s'; git -C D:\repos\memos tag --sort=-creatordate | Select-Object -First 5]
assistant: [tool: list_dir · {"target_directory": "D:\\repos\\memos"}]

[tool: read_file · {"filePath": "D:\\repos\\memos\\README.md", "limit": 80}]
assistant: [tool: read_file · {"filePath": "D:\\repos\\memos\\CONTEXT.md"}]

[tool: read_file · {"filePath": "D:\\repos\\memos\\AGENTS.md"}]
assistant: memos 定位是自托管短笔记应用（Go + React），与本仓领域不同，但有几个直接相关面：`server/mcp/`（MCP 集成）、`filter/`（CEL→SQL 编译器）、`markdown/`（语法扩展）、`provider/ai`。深入读代码。

[tool: list_dir · {"target_directory": "D:\\repos\\memos\\server\\mcp"}]

[tool: list_dir · {"target_directory": "D:\\repos\\memos\\filter"}]

[tool: list_dir · {"target_directory": "D:\\repos\\memos\\provider\\ai"}]

[tool: list_dir · {"target_directory": "D:\\repos\\memos\\markdown"}]
assistant: [tool: read_file · {"filePath": "D:\\repos\\memos\\server\\mcp\\README.md"}]

[tool: read_file · {"filePath": "D:\\repos\\memos\\server\\mcp\\service.go"}]
assistant: MCP 实现很有料（OpenAPI 驱动 + 进程内回环调用 REST API）。继续看 filter CEL 编译器与 AI provider。

[tool: read_file · {"filePath": "D:\\repos\\memos\\filter\\README.md"}]

[tool: read_file · {"filePath": "D:\\repos\\memos\\provider\\ai\\ai.go"}]

[tool: list_dir · {"target_directory": "D:\\repos\\memos\\server\\mcp\\evals"}]
assistant: [tool: read_file · {"filePath": "D:\\repos\\memos\\server\\mcp\\evals\\README.md"}]

[tool: read_file · {"filePath": "D:\\repos\\memos\\server\\mcp\\adapter.go"}]
assistant: [tool: list_dir · {"target_directory": "D:\\repos\\memos\\markdown\\extensions"}]

[tool: list_dir · {"target_directory": "D:\\repos\\memos\\internal"}]

[tool: list_dir · {"target_directory": "D:\\repos\\memos\\store"}]
assistant: [tool: read_file · {"filePath": "D:\\repos\\memos\\store\\doc.go"}]

[tool: read_file · {"filePath": "D:\\repos\\memos\\store\\driver.go", "limit": 120}]

[tool: read_file · {"filePath": "D:\\repos\\memos\\markdown\\extensions\\tag.go"}]
assistant: [tool: read_file · {"filePath": "D:\\repos\\memos\\store\\store.go", "limit": 150}]

[tool: read_file · {"filePath": "D:\\repos\\memos\\store\\cache.go", "limit": 100}]
assistant: [tool: search_file · *.go]

[tool: read_file · {"filePath": "D:\\repos\\memos\\internal\\identifier\\identifier.go"}]
assistant: [tool: read_file · {"filePath": "D:\\repos\\memos\\store\\cache\\cache.go"}]

[tool: list_dir · {"target_directory": "D:\\repos\\memos\\internal\\identifier"}]
assistant: [tool: read_file · {"filePath": "D:\\repos\\memos\\internal\\identifier\\resource_name.go"}]

[tool: read_file · {"filePath": "D:\\repos\\memos\\server\\mcp\\catalog.go", "limit": 120}]
assistant: memos 侧核心机制已清楚。现在到本仓证伪：检查 CodeWiki MCP 工具注册表是否已有 annotations / structuredContent / 工具级 eval 等能力。

[tool: search_content · d:\repos\CodeWiki-Plus\codewiki\mcp]

[tool: list_dir · {"target_directory": "d:\\repos\\CodeWiki-Plus\\codewiki\\mcp"}]
assistant: [tool: search_content · d:\repos\CodeWiki-Plus\codewiki\mcp]

[tool: read_file · {"filePath": "d:\\repos\\CodeWiki-Plus\\codewiki\\mcp\\registry.py", "limit": 100}]
assistant: [tool: search_content · d:\repos\CodeWiki-Plus\codewiki\mcp]

[tool: search_content · d:\repos\CodeWiki-Plus\codewiki\mcp]
assistant: [tool: read_file · {"filePath": "d:\\repos\\CodeWiki-Plus\\codewiki\\mcp\\registry.py", "offset": 100, "limit": 60}]

[tool: search_content · d:\repos\CodeWiki-Plus\codewiki\mcp]
assistant: [tool: read_file · {"filePath": "d:\\repos\\CodeWiki-Plus\\codewiki\\mcp\\cache.py", "limit": 60}]

[tool: search_content · d:\repos\CodeWiki-Plus\codewiki\mcp]
assistant: [tool: read_file · {"filePath": "d:\\repos\\memos\\server\\mcp\\result.go"}]

[tool: read_file · {"filePath": "d:\\repos\\memos\\server\\mcp\\validation.go", "limit": 80}]
assistant: [tool: read_file · {"filePath": "D:\\repos\\memos\\server\\mcp\\evals\\harness.go", "limit": 120}]

[tool: read_file · {"filePath": "D:\\repos\\memos\\filter\\README.md"}]
assistant: [tool: list_dir · {"target_directory": "D:\\repos\\memos\\server\\mcp\\evals"}]

[tool: read_file · {"filePath": "D:\\repos\\memos\\server\\mcp\\service.go", "limit": 120}]
assistant: [tool: read_file · {"filePath": "D:\\repos\\memos\\server\\mcp\\evals\\README.md"}]

[tool: read_file · {"filePath": "D:\\repos\\memos\\server\\mcp\\evals\\memos_eval.xml", "limit": 80}]
assistant: [tool: read_file · {"filePath": "D:\\repos\\memos\\server\\mcp\\catalog.go", "offset": 120, "limit": 150}]

[tool: read_file · {"filePath": "D:\\repos\\memos\\server\\mcp\\adapter.go", "limit": 100}]
assistant: [tool: search_content · D:\repos\memos\server\mcp]

[tool: read_file · {"filePath": "D:\\repos\\memos\\store\\driver.go", "limit": 80}]
assistant: [tool: search_content · D:\repos\memos\server\mcp]
assistant: [tool: read_file · {"filePath": "D:\\repos\\memos\\server\\mcp\\catalog.go", "offset": 1, "limit": 80}]

[tool: read_file · {"filePath": "D:\\repos\\memos\\server\\mcp\\README.md"}]
assistant: memos 侧材料已齐。现在核对本仓现状，确认哪些机制缺失（annotations / structuredContent / 工具级 eval）。

[tool: search_content · d:\repos\CodeWiki-Plus\codewiki\mcp]

[tool: search_content · d:\repos\CodeWiki-Plus\codewiki\mcp]
assistant: [tool: search_content · d:\repos\CodeWiki-Plus\codewiki\mcp]

[tool: read_file · {"filePath": "d:\\repos\\CodeWiki-Plus\\codewiki\\mcp\\registry.py", "offset": 3190, "limit": 80}]
assistant: [tool: read_file · {"filePath": "d:\\repos\\CodeWiki-Plus\\codewiki\\mcp\\server.py", "offset": 80, "limit": 80}]
assistant: [tool: search_content · d:\repos\CodeWiki-Plus\codewiki\mcp]
assistant: [tool: search_content · d:\repos\CodeWiki-Plus\codewiki\mcp]
assistant: [tool: search_content · d:\repos\CodeWiki-Plus\codewiki\mcp]
assistant: [tool: read_file · {"filePath": "d:\\repos\\CodeWiki-Plus\\codewiki\\mcp\\registry.py", "offset": 3075, "limit": 70}]
assistant: [tool: search_content · d:\repos\CodeWiki-Plus\codewiki\mcp]
assistant: [tool: search_content · d:\repos\CodeWiki-Plus\codewiki\mcp]
assistant: [tool: search_content · d:\repos\CodeWiki-Plus\codewiki\mcp]
assistant: [tool: search_content · d:\repos\CodeWiki-Plus\codewiki\mcp]
assistant: [tool: search_content · d:\repos\CodeWiki-Plus\codewiki\mcp]
assistant: [tool: read_file · {"filePath": "d:\\repos\\CodeWiki-Plus\\codewiki\\mcp\\registry.py", "limit": 100}]
assistant: [tool: read_file · {"filePath": "d:\\repos\\CodeWiki-Plus\\codewiki\\mcp\\registry.py", "offset": 100, "limit": 80}]
assistant: 本仓现状已核实：`Tool` 仅 name/description/inputSchema，无 annotations、无 outputSchema、无 structuredContent（`registry.py:106-155`、`server.py:106-119`）。看一下本任务既有调研文档的格式约定。

[tool: search_file · *调研*]
assistant: [tool: read_file · {"filePath": "d:\\repos\\CodeWiki-Plus\\docs\\llm-wiki-compiler-调研与借鉴分析.md", "limit": 80}]
assistant: 格式已明确。补齐 memos 版本基线与剩余两个机制面（markdown 扩展、AI provider）。

[tool: execute_command · git -C D:\repos\memos describe --tags 2>$null; git -C D:\repos\memos log -1 --format='%H %ci'; (Get-Content D:\repos\memos\package.jso…

[tool: read_file · {"filePath": "D:\\repos\\memos\\provider\\ai\\ai.go"}]
assistant: [tool: execute_command · git -C D:\repos\memos describe --tags; git -C D:\repos\memos log -1 --format='%H %ci']

[tool: read_file · {"filePath": "D:\\repos\\memos\\markdown\\extensions\\tag.go"}]
assistant: [tool: search_content · D:\repos\memos\server\router\ai]

[tool: list_dir · {"target_directory": "D:\\repos\\memos\\server\\router\\ai"}]
assistant: [tool: search_content · D:\repos\memos]
assistant: [tool: read_file · {"filePath": "D:\\repos\\memos\\server\\api\\v1\\ai_service.go", "limit": 100}]
assistant: 材料齐了。memos 的 AI provider 只是音频转写（STT），与本仓无关；价值集中在 MCP server 工程。写调研报告。

[tool: write_to_file · {"filePath": "d:\\repos\\CodeWiki-Plus\\docs\\memos-调研与借鉴分析.md", "content": "# memos 调研与借鉴分析\n\n> 调研日期：2026-09-19 · 任务：他山之石 · 方法：克隆源码读代码…
assistant: [tool: mcp_call_tool · {"serverName": "codewiki", "toolName": "add_task_memory", "arguments": "{\"task_id\": \"他山之石\", \"content\": \"完成 memos（usememos/memos，H…
assistant: [tool: write_to_file · {"filePath": "d:\\repos\\CodeWiki-Plus\\.codebuddy\\memory\\2026-09-19.md", "content": "# 2026-09-19\n\n## memos 调研（任务：他山之石）\n- 克隆 D:\\r…
assistant: 调研完成，报告已落盘 `docs/memos-调研与借鉴分析.md`。

## 核心结论

**memos 是自托管笔记应用（Go + React，40k+ star），业务上与本仓无重叠，但其 `server/mcp/` 是迄今调研项目里 MCP 协议合规工程最完善的样本**——每个机制都对应真实 issue，不是 speculative 设计。

### 值得借鉴的机制（代码核对）

1. **工具 annotations**（`catalog.go:371-401`）：从 HTTP 方法推导 readOnly/destructive/idempotent hint，再用覆盖表修正方法启发式错的地方（如 PATCH 整体替换 → idempotent+destructive）。
2. **structuredContent 规范化**（`result.go:11-36`）：成功结果强制对象形（裸数组→`{"result":[...]}`），修 strict 客户端拒绝裸数组的 #6022；**错误结果刻意不带 structuredContent**，避免 strict 客户端拿错误载荷对成功 outputSchema 校验（#6139）。
3. **任务级 eval**（`evals/memos_eval.xml`）：15 个 QA 钉在确定性种子数据上，测的不是管道而是「LLM 组合工具能否答对真实问题」——工具描述的回归网。
4. **OpenAPI 单一事实源 + 白名单 fail-fast**：覆盖表引用不存在的 operation 时启动即报错，防静默失配（`catalog.go:152-169`）。

### 处置表摘要

| 处置 | 条目 |
|------|------|
| **absorbed（建议立项）** | registry `_register` 加 annotations 参数：写类工具（confirm_note/reject_note/edit_doc_file 等）标 `destructiveHint`，查询类标 `readOnlyHint`——小改动，宿主侧直接展示破坏性警告 |
| **deferred** | structuredContent/outputSchema + 错误形状（同根，等 strict 宿主出现）；任务级 eval（并入质量量化主线，与 llm-wiki-compiler 调研 #1/#9 合流） |
| **excluded** | OpenAPI 驱动（本仓无 REST 层）、CEL→SQL（无 SQL 存储）、goldmark AST（markdown 是存储非渲染）、目录 TTL（stdio 无 discover 流）等 6 条 |

基线：v0.31.0-rc.2-16-g7e3d3c6（2026-09-19），本地克隆 `D:\repos\memos`，下次增量调研以此为基线。
user: <manually_attached_skills>
Please use the use_skill tool to invoke this skill.

name: grill-with-docs
description: A relentless interview to sharpen a plan or design, which also creates docs (ADR's and glossary) as we go.
</manually_attached_skills>

@command://grill-with-docs  值得借鉴吗
assistant: [tool: use_skill · grill-with-docs]
assistant: [tool: use_skill · grilling]
assistant: [tool: use_skill · domain-modeling]
assistant: 收到——用 grill 模式来拷问「memos 的东西到底值不值得借鉴」。我先把处置表里的每个裁决变成设计树上的节点，第一轮把当前 frontier 上的问题一次问全。

先亮我的立场：**「值得借鉴」不是整体判断，是逐条裁决**。我的报告给了 1 absorbed / 3 deferred / 6 excluded，现在逐条压力测试。

---

❓ **Q1** - **借鉴的范围**：你问「值得借鉴吗」——是只讨论那条 absorbed（工具 annotations），还是想借这次把 3 条 deferred 也重新裁决一遍？

选项：
- A. 只谈 annotations，deferred 维持原判
- B. annotations + 重新审视 deferred（structuredContent/错误形状、任务级 eval）

➡️ 推荐选 A。deferred 两条都有明确的触发条件（strict 宿主出现、质量量化主线立项），条件没变，重开讨论是浪费。

---

❓ **Q2** - **annotations 的实际收益是否可观测**：这是事实问题，我来查——本仓的宿主（CodeBuddy IDE）到底会不会消费 `destructiveHint` 并给用户展示警告？如果宿主根本不理会 annotations，这条 absorbed 的「收益直接」就是虚的，只剩「未来兼容」价值。

➡️ 我先按「会消费」假设推进，但这条我会去核实（查 cbm_client 与宿主行为），核实结果可能推翻 Q3 的裁决。

---

❓ **Q3** - **annotations 现在做还是挂起**：如果 Q2 核实宿主确实消费，改动本身很小（`registry.py` 的 `_register` 加一个可选参数 + 给写类工具打标）。但「小改动」不等于「现在做」——现在做的理由是什么？有正在进行的 registry 变更可以搭车吗？还是为了「顺手」而做（Team Doctrine：成本可见性优先于新造能力）？

选项：
- A. 现在立项，单独小 PR 落地
- B. 挂起，等下次 registry 契约变更时搭车
- C. 不做，等宿主侧出现真实需求信号

➡️ 推荐 B。单独为 annotations 开一次契约变更不符合「搭收敛点」原则；但 C 太保守——改动确实小且方向确定。

---

❓ **Q4** - **destructive 的判定标准**：哪些工具标 `destructiveHint`？memos 的标准是「覆盖既有状态」。套到本仓：
- 明确 destructive：`reject_note`、`delete_task`、`edit_doc_file`（覆盖原文）
- 边界争议：`confirm_note`（改变状态但用户显式发起）、`ingest_note`（新建不覆盖）、`batch_set_status`（批量改状态）

判定标准选哪个：
- A. memos 标准：覆盖/删除既有状态 → destructive；纯新建 → 非 destructive
- B. 更宽：一切改变持久化状态的操作都标 destructive（宁严勿松）
- C. 更窄：只有不可逆操作（删除、覆盖）才标

➡️ 推荐 A。annotations 是给宿主的提示不是安全机制（memos 注释原话），B 会让警告泛滥失去信号价值，C 漏掉 `edit_doc_file` 这类可逆但破坏性的操作。

---

❓ **Q5** - **术语入册**：这轮讨论引入了「工具 annotations」「structuredContent」两个 MCP 协议术语。它们要不要进 `CONTEXT.md` 词汇表？我的倾向：**不进**——CONTEXT.md 是本仓领域词汇表，MCP 协议术语是外部协议事实，写进去只会稀释。裁决本身（annotations 判定标准）如果落定，进 ADR 或 Wiki 笔记更合适。

➡️ 推荐不进 CONTEXT.md，Q4 的判定标准若定案则记入 Wiki。

---

回答 Q1-Q5（Q2 我自己去核实），我们再进下一轮。
user: 按推荐
assistant: 按推荐执行。先核实 Q2 事实：本仓用的 `mcp` Python SDK 的 `Tool` 类型是否支持 annotations 字段（宿主消费的前提是协议层能传出去）。

[tool: search_content · d:\repos\CodeWiki-Plus\.venv\Lib\site-packages\mcp\types.py]
assistant: SDK 层支持确认（`mcp/types.py:1329`，`Tool.annotations: ToolAnnotations | None`）。现在看 registry 的 `Tool(...)` 构造点，确定改动方案。

[tool: search_content · d:\repos\CodeWiki-Plus\codewiki\mcp]

[tool: search_content · d:\repos\CodeWiki-Plus\codewiki\mcp]
assistant: [tool: search_content · d:\repos\CodeWiki-Plus\codewiki\mcp]

[tool: search_content · d:\repos\CodeWiki-Plus\codewiki\mcp]
assistant: [tool: read_file · {"filePath": "d:\\repos\\CodeWiki-Plus\\codewiki\\mcp\\registry.py", "offset": 40, "limit": 70}]
assistant: Q2 核实结果：SDK 协议层就绪——`mcp/types.py:1329` 的 `Tool` 已有 `annotations: ToolAnnotations | None` 字段，`readOnlyHint`/`destructiveHint` 均在（`mcp/types.py:1247-1266`）。宿主是否消费未证实，但改动方向无协议障碍。

按推荐落定：Q1=A、Q3=B（挂起搭车）、Q4=A（memos 标准）、Q5=不进 CONTEXT.md。现在把裁决沉淀：先查重，再更新调研报告、落草稿笔记。

[tool: mcp_call_tool · {"serverName": "codewiki", "toolName": "query_wiki", "arguments": "{\"mode\": \"check\", \"query\": \"MCP 工具 annotations destructiveHint…
assistant: [tool: mcp_call_tool · {"serverName": "codewiki", "toolName": "ingest_note", "arguments": "{\"note_type\": \"decision\", \"status\": \"draft\", \"title\": \"MC…
assistant: [tool: search_content · d:\repos\CodeWiki-Plus\docs]
assistant: [tool: search_content · d:\repos\CodeWiki-Plus\docs]
assistant: [tool: search_file · *memos*]
assistant: [tool: read_file · {"filePath": "d:\\repos\\CodeWiki-Plus\\docs\\memos-调研与借鉴分析.md", "offset": 40, "limit": 60}]
assistant: [tool: read_lints · {"paths": "d:\\repos\\CodeWiki-Plus\\docs\\memos-调研与借鉴分析.md"}]
assistant: [tool: mcp_call_tool · {"serverName": "codewiki", "toolName": "add_task_memory", "arguments": "{\"task_id\": \"他山之石\", \"content\": \"Grill 轮裁决 memos 调研的 annot…
assistant: Grill 轮裁决已全部落定并沉淀：

## 裁决结果

| 问题 | 裁决 |
|------|------|
| Q1 范围 | A——只谈 annotations，deferred 维持原判 |
| Q2 事实核实 | **SDK 层已支持**：`mcp/types.py:1329` `Tool.annotations: ToolAnnotations`，`readOnlyHint`/`destructiveHint` 字段齐全（`mcp/types.py:1247-1266`）。宿主消费行为未证实，但协议层无障碍 |
| Q3 时机 | B——**挂起搭车**，等下次 registry 契约变更时顺路落地，不单独立项 |
| Q4 判定标准 | A——memos「覆盖/删除既有状态 → destructive」：destructive 集合 = {`edit_doc_file`, `reject_note`, `delete_task`}；`confirm_note`/`ingest_note`/`batch_set_status` 不标（宁严勿松会让警告泛滥失去信号价值） |
| Q5 术语 | 不进 `CONTEXT.md`——MCP 协议术语是外部协议事实，不是本仓领域词汇 |

## 已沉淀

1. **草稿笔记**（待你确认）：`notes/2026-09-19-mcp-工具-annotations-挂起待搭车sdk-已支持判定标准采用-memos-覆盖既有状态说.md`——记录了挂起决策、判定标准、SDK 核实结果、实现时的 destructive 集合清单。
2. **报告同步**：`docs/mos-调研与借鉴分析.md` 处置表 #1 与结论段已从「建议立项」改为「挂起搭车」。

要现在 `confirm_note` 把这条决策笔记转正吗？还是先留着草稿状态？
user: 所以有值得借鉴落地的项吗
assistant: 直接回答：**现在没有需要立即落地的项。**

Grill 轮之后的最终状态：

| 项 | 裁决 | 落地时机 |
|----|------|---------|
| 工具 annotations | 唯一 absorbed，但**挂起搭车** | 等下次 registry 契约变更时顺路做（SDK 已支持，改动方案已定，就差一个搭车点） |
| structuredContent / 错误形状 | deferred | 等 strict 宿主出现（当前宿主不校验，做了无收益） |
| 任务级 eval | deferred | 并入质量量化主线（与 llm-wiki-compiler 调研 #1/#9 同根，等那条线立项） |
| 其余 6 条 | excluded | 前提不成立或本仓已有等价实现 |

memos 的价值在于**把「值得借鉴」的判定标准校准得更准了**：36 个工具的 MCP server，真正能搬过来的只有协议层三个小机制，且每一个都因为「触发条件未到」而不该现在动手。这符合 Team Doctrine 的「成本可见性优先于新造能力」——改动方向确定 ≠ 现在做。

唯一可执行的后续动作是：**下次有人动 `registry.py` 契约时（比如 structuredContent 落地），把 annotations 一起带上**。这条已经写进草稿笔记和任务记忆，不会丢。
