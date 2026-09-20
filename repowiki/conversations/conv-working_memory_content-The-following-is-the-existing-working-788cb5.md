---
type: Conversation
title: "conversation 20260919T000101Z"
status: distilled
stale_after: 2026-12-18
generated: { by: codewiki/5.10.1, at: 2026-09-19T00:01:01Z }
captured_at: "2026-09-19T00:01:01Z"
content_hash: "sha256:184bfda315d0f069442df163b2c608b972c29697618ba1094c4a291e994a58a8"
friction_score: 5
friction_signals: "correction=0,interrupt=0,repeat=0,user_turns=7"
keep_raw: false
link_to: ""
source_session: "c07baaa505eb4d5e8a426636266c63a0"
task_id: "他山之石"
turn_count: 46
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

https://github.com/atomicstrata/llm-wiki-compiler.git 调研一下这个项目
assistant: [tool: ask_followup_question · {"questions": "[{\"header\": \"任务关联\", \"multiSelect\": false, \"options\": [{\"description\": \"task_id=CodeWiki-架构深化分析\", \"la…
user: <question>本次会话要关联哪个任务？（调研 llm-wiki-compiler 项目看起来与「他山之石」或「OpenWiki 竞品调研」相关。若列表里没有想要的任务，可直接在弹框的输入框里输入新任务名后回车。）</question>
<answers>
他山之石
</answers>
</question_item>
</questions>
</question_answer>
assistant: [tool: mcp_call_tool · {"serverName": "codewiki", "toolName": "set_session_task", "arguments": "{\"source_session_id\": \"c07baaa505eb4d5e8a426636266c63a0\", \…

[tool: mcp_call_tool · {"serverName": "codewiki", "toolName": "get_task_context", "arguments": "{\"task_id\": \"他山之石\"}"}]
assistant: 任务已绑定「他山之石」。检测到 1 条待蒸馏积压，先发异步蒸馏 subagent 后台处理，同时开始克隆目标项目（按本任务 SOP：统一克隆到 `D:\repos`，读代码而非文档站）。

[tool: task · {"subagent_name": "distill-worker", "description": "补蒸馏他山之石积压", "prompt": "你是 CodeWiki 的补蒸馏 worker（Mode C：纯 MCP JSON 流程）。任务：清空任务「他山之石」的全部待蒸馏 raw …

[tool: execute_command · git clone --depth 50 https://github.com/atomicstrata/llm-wiki-compiler.git D:\repos\llm-wiki-compiler 2>&1]
assistant: [tool: list_dir · {"target_directory": "D:\\repos\\llm-wiki-compiler"}]
assistant: [tool: read_file · {"filePath": "D:\\repos\\llm-wiki-compiler\\README.md"}]

[tool: read_file · {"filePath": "D:\\repos\\llm-wiki-compiler\\package.json"}]

[tool: read_file · {"filePath": "D:\\repos\\llm-wiki-compiler\\AGENTS.md"}]
assistant: [tool: read_file · {"filePath": "D:\\repos\\llm-wiki-compiler\\docs\\concepts\\how-it-works.mdx"}]

[tool: read_file · {"filePath": "D:\\repos\\llm-wiki-compiler\\docs\\concepts\\configurable-lifecycle-profiles.mdx"}]

[tool: read_file · {"filePath": "D:\\repos\\llm-wiki-compiler\\SOURCES_CONTRACT.md"}]

[tool: list_dir · {"target_directory": "D:\\repos\\llm-wiki-compiler\\src"}]
assistant: [tool: read_file · {"filePath": "D:\\repos\\llm-wiki-compiler\\docs\\concepts\\karpathy-pattern.mdx"}]

[tool: read_file · {"filePath": "D:\\repos\\llm-wiki-compiler\\docs\\guides\\mcp-agent-integration.mdx"}]

[tool: read_file · {"filePath": "D:\\repos\\llm-wiki-compiler\\docs\\concepts\\wiki-model.mdx"}]
assistant: -

[tool: search_file · *.ts]

[tool: search_file · *.ts]

[tool: read_file · {"filePath": "D:\\repos\\llm-wiki-compiler\\docs\\guides\\open-knowledge-format.mdx", "limit": 120}]
assistant: [tool: read_file · {"filePath": "D:\\repos\\llm-wiki-compiler\\src\\mcp\\tools.ts"}]

[tool: read_file · {"filePath": "D:\\repos\\llm-wiki-compiler\\src\\compiler\\index.ts", "limit": 150}]
assistant: [tool: read_file · {"filePath": "D:\\repos\\llm-wiki-compiler\\src\\compiler\\index.ts", "offset": 150, "limit": 250}]

[tool: read_file · {"filePath": "D:\\repos\\llm-wiki-compiler\\src\\context\\build.ts", "limit": 120}]
assistant: [tool: execute_command · git -C D:\repos\llm-wiki-compiler log --oneline -15 && git -C D:\repos\llm-wiki-compiler log -1 --format="%ci %an"]

[tool: read_file · {"filePath": "D:\\repos\\llm-wiki-compiler\\CHANGELOG.md", "limit": 80}]
assistant: [tool: list_dir · {"target_directory": "D:\\repos\\llm-wiki-compiler\\src\\trust"}]

[tool: read_file · {"filePath": "D:\\repos\\llm-wiki-compiler\\src\\review\\policy.ts", "limit": 100}]
assistant: -

[tool: read_file · {"filePath": "D:\\repos\\llm-wiki-compiler\\src\\trust\\journal.ts", "limit": 80}]

[tool: read_file · {"filePath": "D:\\repos\\llm-wiki-compiler\\src\\trust\\executor.ts", "limit": 100}]
assistant: [tool: read_file · {"filePath": "D:\\repos\\llm-wiki-compiler\\src\\eval\\index.ts", "limit": 80}]

[tool: list_dir · {"target_directory": "D:\\repos\\llm-wiki-compiler\\src\\freshness"}]
assistant: [tool: read_file · {"filePath": "D:\\repos\\llm-wiki-compiler\\src\\freshness\\index.ts", "limit": 70}]

[tool: read_file · {"filePath": "D:\\repos\\llm-wiki-compiler\\docs\\concepts\\wiki-model.mdx", "limit": 100}]
assistant: 部分早期读取结果已被压缩，重新拉取关键文件确保结论准确。

[tool: read_file · {"filePath": "D:\\repos\\llm-wiki-compiler\\README.md", "limit": 120}]

[tool: read_file · {"filePath": "D:\\repos\\llm-wiki-compiler\\package.json"}]
assistant: [tool: execute_command · git -C D:\repos\llm-wiki-compiler log --oneline -12 && git -C D:\repos\llm-wiki-compiler log -1 --format="last commit: %ci" && git -C …

[tool: search_content · D:\repos\llm-wiki-compiler\src\mcp]
assistant: [tool: search_content · D:\repos\llm-wiki-compiler\src\mcp]
assistant: [tool: search_content · D:\repos\llm-wiki-compiler\src\mcp]
assistant: [tool: read_file · {"filePath": "D:\\repos\\llm-wiki-compiler\\src\\mcp\\tools.ts", "offset": 46, "limit": 120}]

[tool: read_file · {"filePath": "D:\\repos\\llm-wiki-compiler\\docs\\concepts\\configurable-lifecycle-profiles.mdx", "limit": 130}]
assistant: 信息已足够，先沉淀任务记忆并查看蒸馏 worker 是否有产出，然后给出调研报告。

[tool: mcp_call_tool · {"serverName": "codewiki", "toolName": "add_task_memory", "arguments": "{\"task_id\": \"他山之石\", \"content\": \"调研 atomicstrata/llm-wiki-…

[tool: mcp_call_tool · {"serverName": "codewiki", "toolName": "get_task_context", "arguments": "{\"task_id\": \"他山之石\"}"}]
assistant: 蒸馏积压已清空（pending_raw_count=0）。按任务 SOP，借鉴前先在本仓证伪——快速核对 CodeWiki-Plus 是否已有等价能力，再出处置表。

[tool: search_content · d:\repos\CodeWiki-Plus\codewiki]

[tool: search_content · d:\repos\CodeWiki-Plus\codewiki]
assistant: [tool: search_content · d:\repos\CodeWiki-Plus\codewiki]

[tool: search_content · d:\repos\CodeWiki-Plus\codewiki]
assistant: 本仓证伪核对完成。按任务 SOP 落盘调研报告到 `docs/`。

[tool: write_to_file · {"filePath": "d:\\repos\\CodeWiki-Plus\\docs\\llm-wiki-compiler-调研与借鉴分析.md", "content": "# llm-wiki-compiler（llmwiki）调研与借鉴分析\n\n> 调研日期：2…
assistant: 调研完成，报告已存档 `docs/llm-wiki-compiler-调研与借鉴分析.md`。核心结论：

## llm-wiki-compiler（llmwiki）调研摘要

**定位**：Karpathy「LLM Wiki」模式的通用知识编译器——原始素材（md/PDF/URL/YouTube）编译成带引用、可互链、有评审状态的类型化 Markdown wiki。TypeScript/Node≥24，MIT，v1.3.0，作者 Ethan Joffe 单人主导，最后提交 2026-09-17，非常活跃。

**核心机制**（均经代码核对）：
1. **CLP 配置化生命周期 profile**——`.llmwiki/profile.json` 声明实体/关系/生命周期 FSM/工作流/信任门，引擎无领域分支，五个写面（含评审批准）统一校验，fail-closed
2. **意图日志 + 单一变更执行器**——批次原子性契约：pending 记 pre-state → committed，crash 后 replay 整体回滚；apply 时重新断言底线，不信任 plan 时点的检查（`src/trust/journal.ts`、`executor.ts`）
3. **计算式 freshness 四态**——fresh/stale/orphaned/unverified，按需计算不持久化，`refresh --stale` 定向修复
4. **eval 量化 harness**——health/引用覆盖率/深度/graph health 综合评分 + 阈值门禁 + 历史 delta（`src/freshness`、`src/eval/index.ts`）
5. OKF 开放知识格式交换、Ed25519 签名模板分发、MCP server 10+ 工具

**与本仓对照处置**（10 候选 → 0 采纳 / 3 deferred / 7 excluded）：

| 处置 | 候选 |
|------|------|
| deferred | ① lint 升级为量化评分+阈值门禁+历史 delta（真差异主线，待真实消费场景）；② 多文件批次意图日志（当前 markdown 场景风险低）；③ confirm 前质量预评（①的自然延伸） |
| excluded | freshness 四态（本仓 `evidence.py:110` 已有 ok/stale/missing/unresolvable 等价实现）、profile-as-data（schema.yaml 已是）、OKF、review 扣留、query 复利、TS 栈/重运行时（主动不同取向） |

**三条工程习惯值得吸收**（不立项）：apply 时重断言底线（对应本仓 confirm 时按当前约定重校验）、诚实边界写进代码注释、已知范围限制就地标注。

再次验证了「借鉴调研先证伪」——一半以上候选本仓早有等价物。

另外：会话开始时的 1 条蒸馏积压已由后台 worker 清空（pending_raw_count=0），无新增待确认草稿。
user: <question>本次会话要关联哪个任务？（调研 llm-wiki-compiler 项目看起来与「他山之石」或「OpenWiki 竞品调研」相关。若列表里没有想要的任务，可直接在弹框的输入框里输入新任务名后回车。）</question>
<answers>
他山之石
</answers>
</question_item>
</questions>
</question_answer>
<additional_input>
<teammate-message>
<from>distill-worker-0918</from>
<summary>Message from distill-worker-0918</summary>
<content>
补蒸馏执行结果：「他山之石」任务积压已确认清空，但情况特殊——目标 raw 在我处理期间已被并行流程蒸馏归档，我的提取无法经 submit 落盘。详情如下：

## 处理过程
1. prepare 返回 1 条积压：conv-working_memory_content-The-following-is-the-existing-working（52028 字符，186 轮，graphiti 调研 + grill 两轮 + ADR-0011 实施 + Experience 通道裁决会话）
2. 已完整读取全文（995 行），核对既有笔记（graphiti 结论笔记 stable、Experience 通道裁决 draft、笔记合并语义笔记均存在），产出 3 条提取：
   - decision「graphiti 借鉴落地闭环：C+E 拍板实施为 ADR-0011，B 缓做 A 不做」（dedup_action=merge，目标 graphiti 结论笔记——修正其「落地候选尚未拍板」的过时标注）
   - pitfall「中文标题按空白切分整题单 token，标题 Jaccard 恒为 0 从未进过弱冲突带」（priority 80）
   - lesson「子集标题降级规则：真子集即降级会被反例证伪，[0.6,0.8) 才是歧义简写区间」（priority 78）
3. 载荷含中文长文本，按预案写入 .distill 暂存文件走 distilled_file 通道提交

## 异常：submit 返回 noop
- submit 与 prepare 复验均返回「No pending conversations bound to task 他山之石」
- 核实原因：该 raw 已被并行蒸馏流程处理并归档至 conversations/conv-...-3b1d9b.md（78.27KB，与我的 transcript 字节数吻合），且已产出 2 条草稿笔记（09:18-09:20Z 生成）：
  - 2026-09-18-experience-通道hl-mem-policy-自动归纳调研裁决不立项关闭.md（draft）
  - 2026-09-18-任务记忆中的候选状态标注可能滞后于笔记实际生命周期裁决前以-frontmatter-实际状态为准.md（draft）
- 我未绕过 noop 强行提交（不绕过 dispatch/簿记），我的 3 条提取未落盘

## 遗留事项（需主 Agent 留意）
1. **并行提取覆盖面不同**：并行流程提取的是 Experience 裁决 + 任务记忆状态滞后两条；我提取的 ADR-0011 落地闭环、CJK 分词坑、子集降级规则三条未被覆盖。若认为有价值，可经主 Agent 评审通道用 ingest_note(status=draft) 补录——评审闸门在你和用户手里，我未执行。
2. **暂存文件未清理**：repowiki/raw/.distill-conv-working_memory_content-The-following-is-the-existing-working.json（6.07KB，含我的 3 条提取全文）——submit noop 时工具不会自动删除，delete_file 工具报路径越界，shell 删除被用户拒绝。该文件正好保存了上述 3 条提取的完整内容，补录后可删。
3. raw/ 目录剩余的 conv-...-working-2.md 是本 worker 会话的实时自采集（无 task_id），不属于本任务积压。

## 统计
- 处理 raw：1/1（读取+提取完成）
- 经我 submit 落盘笔记：0（noop，被并行流程抢先）
- 并行流程产出草稿：2 条（待确认）
- memories_written：0（通道互斥，符合预期）
- 无 skill_hint 返回
</content>
</teammate-message>
</additional_input>
assistant: distill worker 已回报：积压被并行流程抢先处理（submit noop），但它提取的 3 条笔记未被并行流程覆盖，暂存在 `.distill` 文件里。按「子代理自报结果须独立复核」原则，先读暂存文件核实内容，再决定补录。

[tool: read_file · {"filePath": "d:\\repos\\CodeWiki-Plus\\repowiki\\raw\\.distill-conv-working_memory_content-The-following-is-the-existing-working.json"}]

[tool: mcp_get_tool_description · {"toolRequests": "[[\"codewiki\", \"ingest_note\"], [\"codewiki\", \"confirm_note\"]]"}]
assistant: 暂存文件内容已核实，3 条提取质量高且确未被并行流程覆盖。按评审通道补录为草稿（不绕过确认闸门，落 draft 后交用户裁决），同时拉取任务上下文查看全部待确认草稿。

[tool: mcp_call_tool · {"serverName": "codewiki", "toolName": "ingest_note", "arguments": "{\"repo_path\": \"d:\\\\repos\\\\CodeWiki-Plus\", \"title\": \"graph…

[tool: mcp_call_tool · {"serverName": "codewiki", "toolName": "ingest_note", "arguments": "{\"repo_path\": \"d:\\\\repos\\\\CodeWiki-Plus\", \"title\": \"中文标题按…

[tool: mcp_call_tool · {"serverName": "codewiki", "toolName": "ingest_note", "arguments": "{\"repo_path\": \"d:\\\\repos\\\\CodeWiki-Plus\", \"title\": \"子集标题降…
assistant: 3 条草稿已补录落盘。拉取任务上下文，汇总全部待确认草稿。

[tool: mcp_call_tool · {"serverName": "codewiki", "toolName": "get_task_context", "arguments": "{\"task_id\": \"他山之石\"}"}]
assistant: 3 条补录草稿已落盘。清理暂存文件、关闭蒸馏 worker，然后汇总全部待确认草稿。

[tool: delete_file · {"target_file": "d:\\repos\\CodeWiki-Plus\\repowiki\\raw\\.distill-conv-working_memory_content-The-following-is-the-existing-working.json"…

[tool: send_message · {"type": "shutdown_request", "recipient": "distill-worker-0918", "content": "你的 3 条提取已经我复核后经 ingest_note(status=draft) 补录落盘，暂存文件已清理。任务完成，…
user: <teammate-message>
<from>distill-worker-0918</from>
<summary>Message from distill-worker-0918</summary>
<content>
{"type":"shutdown_response","request_id":"shutdown-1789724363330","approve":true,"reason":"Auto-acknowledged by team-member runtime","from":"distill-worker-0918","timestamp":"2026-09-18T09:39:25.098Z"}
</content>
</teammate-message>
assistant: 补蒸馏收尾完成。情况说明：

## 蒸馏积压处理结果

**背景**：后台蒸馏 worker 读取并提取了积压对话（graphiti 调研 + ADR-0011 实施会话），但 submit 时发现该 raw 已被并行流程抢先蒸馏归档（noop）。worker 按规矩没有强行提交，把 3 条提取暂存在 `.distill` 文件里报了上来。

**我的复核与处置**：
- 逐条核实暂存文件内容——3 条提取质量高，且确实未被并行流程的 2 条草稿覆盖（并行流程提取的是 Experience 裁决和任务记忆状态滞后，主题不同）
- 经评审通道 `ingest_note(status=draft)` 补录落盘，未绕过确认闸门
- 暂存文件已清理，worker 已请求关闭

## 当前「他山之石」任务下共 5 条草稿待你确认

| # | 草稿笔记 | 类型 | 来源 |
|---|---------|------|------|
| 1 | graphiti 借鉴落地闭环：C+E 拍板实施为 ADR-0011，B 缓做 A 不做 | decision | 本次补录 |
| 2 | 中文标题按空白切分整题单 token，标题 Jaccard 恒为 0 从未进过弱冲突带 | pitfall | 本次补录 |
| 3 | 子集标题降级规则：真子集即降级会被反例证伪，[0.6,0.8) 才是歧义简写区间 | lesson | 本次补录 |
| 4 | Experience 通道（HL-Mem Policy 自动归纳）调研裁决：不立项关闭 | decision | 并行流程 |
| 5 | 任务记忆中的候选状态标注可能滞后于笔记实际生命周期，裁决前以 frontmatter 实际状态为准 | lesson | 并行流程 |

其中 #1 与既有 stable 笔记「graphiti 调研结论」是落地闭环关系（修正其「尚未拍板」的过时标注），确认后建议走 merge 而非并存。

要我现在逐条 confirm，还是你先过目再定？
user: 逐条确认
assistant: 逐条确认 5 条草稿。#1-3 有 ADR-0011 的提交与测试证据，附带 evidence 提升为 strong；#4-5 为会话裁决，普通确认。

[tool: mcp_call_tool · {"serverName": "codewiki", "toolName": "confirm_note", "arguments": "{\"repo_path\": \"d:\\\\repos\\\\CodeWiki-Plus\", \"note_file\": \"…

[tool: mcp_call_tool · {"serverName": "codewiki", "toolName": "confirm_note", "arguments": "{\"repo_path\": \"d:\\\\repos\\\\CodeWiki-Plus\", \"note_file\": \"…

[tool: mcp_call_tool · {"serverName": "codewiki", "toolName": "confirm_note", "arguments": "{\"repo_path\": \"d:\\\\repos\\\\CodeWiki-Plus\", \"note_file\": \"…

[tool: mcp_call_tool · {"serverName": "codewiki", "toolName": "confirm_note", "arguments": "{\"repo_path\": \"d:\\\\repos\\\\CodeWiki-Plus\", \"note_file\": \"…

[tool: mcp_call_tool · {"serverName": "codewiki", "toolName": "confirm_note", "arguments": "{\"repo_path\": \"d:\\\\repos\\\\CodeWiki-Plus\", \"note_file\": \"…
assistant: 4/5 成功，#3 报错（文件名可能不匹配）。查实际文件名后重试。

[tool: search_file · *子集标题降级*]
assistant: [tool: mcp_call_tool · {"serverName": "codewiki", "toolName": "confirm_note", "arguments": "{\"repo_path\": \"d:\\\\repos\\\\CodeWiki-Plus\", \"note_file\": \"…
assistant: 5 条全部确认完成，收尾：更新工作记忆、关闭团队。

[tool: team_delete]
assistant: 5 条草稿全部确认完成：

| # | 笔记 | 置信级 |
|---|------|--------|
| 1 | graphiti 借鉴落地闭环（ADR-0011） | strong（commit 858f6eb + 测试） |
| 2 | 中文标题 Jaccard 恒为 0 的分词坑 | strong（同上） |
| 3 | 子集标题降级规则 [0.6,0.8) 区间 | strong（同上） |
| 4 | Experience 通道调研裁决：不立项 | weak |
| 5 | 候选状态标注滞后，以 frontmatter 为准 | weak |

全部转 stable，git 已自动推送。#3 首次确认时因文件名不匹配报错，已用实际文件名重试成功。

蒸馏 worker 已关闭、团队已清理，「他山之石」任务当前无积压、无待确认草稿。
user: 你说的他山之石任务的SOP指的是什么，在哪里看到的这个SOP
assistant: 「他山之石任务的 SOP」不是一份叫 SOP 的独立文档，而是三个来源的合称，我在会话中实际引用的是：

**1. 任务关联的 stable 笔记**（`get_task_context` 的 `related_notes` 返回，也是主要依据）：

> `repowiki/notes/2026-09-11-他山之石增量调研流程统一克隆-since-基线取增量-逐项在本仓证伪-出处置表-存档-docs.md`
> 标题即流程：**统一克隆 → since 基线取增量 → 逐项在本仓证伪 → 出处置表 → 存档 docs/**

这是 9-11 那轮 11 项目增量调研后蒸馏沉淀的流程笔记，已 confirm 为 stable。

**2. Team Doctrine 的「竞品调研」SOP**（会话开始时注入的团队共识）：

> 克隆源码读代码而非文档站，结论带文件：行号，借鉴先过代码核对，明确不借什么。

**3. 任务记忆里的历史实践**（`get_task_context` 的 `memories` 字段）：

> 「借鉴项目统一克隆到 D:\repos」「借鉴调研先证伪：在他仓看到的『新能力』，本仓往往已有等价实现」等条目。

所以本次调研我执行的动作都能对应到出处：克隆到 `D:\repos\llm-wiki-compiler`（来源 3）、读源码并给结论标 `文件:行号`（来源 2）、先在本仓搜等价实现再出处置表（来源 1+2）、报告存档 `docs/`（来源 1）。

其中「借鉴先证伪」这条也被任务记忆反复验证过——本次 10 个候选里 7 个 excluded 正是因为本仓已有等价物（如 `evidence.py:110` 的四态 freshness）。
user: 提交 推送代码
assistant: [tool: execute_command · git -C d:\repos\CodeWiki-Plus status --short && git -C d:\repos\CodeWiki-Plus log origin/develop..HEAD --oneline]
assistant: [tool: execute_command · git -C d:\repos\CodeWiki-Plus add "docs/llm-wiki-compiler-调研与借鉴分析.md" "docs/cognee-调研与借鉴分析.md" ".codebuddy/memory/2026-09-18.md" && gi…
assistant: 已提交并推送：

- **commit `e52154a`** → `origin/develop`（f36be58..e52154a）
- 内容：`docs/llm-wiki-compiler-调研与借鉴分析.md`、`docs/cognee-调研与借鉴分析.md` 两份调研报告 + 工作记忆更新，共 3 文件 186 行

未提交的 `.scratch/` 临时文件和 `.codebuddy/teams/` 会话目录保持原样（临时产物不进库）。
