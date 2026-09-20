# supermemory 调研与借鉴分析

> 调研日期：2026-09-19 · 任务：他山之石 · 方法：克隆源码读代码（D:\repos\supermemory，HEAD 57b430b，2026-09-18），结论均经代码核对，非文档站口径。注意：**核心引擎（learning model + temporal vector-graph）闭源**，开源仓是客户端/集成层（MCP server、tools SDK、可视化、docs、skills），文档站属宣传口径，本文以代码为准。

## 1. 项目概况

| 维度 | 事实 |
|------|------|
| 定位 | AI agent 的记忆与上下文基础设施（商业 SaaS + 开源集成层），"memory and context infrastructure for AI agents" |
| 技术栈 | TypeScript monorepo（bun + turbo），MCP server 跑在 Cloudflare Workers + Durable Objects |
| 仓库结构 | `apps/`（mcp、docs、console 等）、`packages/`（tools SDK、memory-graph 可视化）、`skills/`（agent 技能） |
| 核心模型 | 文档（raw input）→ 管道产出三物：chunks（RAG 溯源）、memories（事实图谱）、profile（常驻摘要）（apps/docs/concepts/how-it-works.mdx:149-159） |
| 隔离 | `containerTag` 硬隔离边界（用户/租户/项目），metadata 是 tag 内软过滤维度（how-it-works.mdx:161-165） |
| 商业模式 | API 计费（operations），`taskType: "superrag"` 跳过记忆管道省 5x 成本（apps/docs/concepts/rules.mdx:38-49） |

领域上 supermemory 是通用记忆基础设施、本仓是代码知识库，但两者在「知识飞轮」上高度同构：采集→蒸馏→确认→检索→沉淀。**本报告重点是其 MCP 层工程与记忆产品概念。**

## 2. 核心机制（代码核对）

### 2.1 记忆图谱：updates / extends / derives + 时间真值
- 三种关系（apps/docs/concepts/graph-memory.mdx:61-101）：**updates**（新事实替换旧事实，`isLatest` 保证检索命中当前值但不抹历史）、**extends**（补充细节，双方皆有效）、**derives**（跨记忆模式推断出从未明说的事实）。
- 记忆原子性：一条记忆只讲一个主题，且总是建立在既有记忆之上（graph-memory.mdx:56-59）。
- 自动遗忘三机制：时间过期（"明天考试"类临时事实）、矛盾时 updates 胜出、噪声过滤（graph-memory.mdx:136-142）。

### 2.2 Dreaming：记忆入图谱的异步二阶段
- 文档 `status: done` 只代表 chunks 可检索；memories 来自第二阶段 **dreaming**（how-it-works.mdx:114-126）。
- 双模式：**dynamic**（默认，相关文档成组蒸馏，记忆从连贯单元而非孤立单条形成，质量更高）vs **instant**（单文档立即入图谱，多计一次 operation，用于 demo）。
- 「成组蒸馏质量高于孤立单条」是明确写进文档的产品结论（graph-memory.mdx:122）。

### 2.3 推断记忆降权 + 审阅队列（与确认闸门同构）
- derives 产出的记忆标 `isInference: true`，**在搜索中降权**，直到人工审阅（apps/docs/recall/memory-review.mdx:8-15）。
- 审阅三动作（memory-review.mdx:28-36）：**approve** → 清除推断标记，按明说事实同权重排序；**decline** → 置 `isForgotten`，从搜索中完全移除（驳回即遗忘）；**undo** → 回到队列重新降权。
- `reviewStatus` 盖章后移出队列，undo 清章并反遗忘。

### 2.4 Profile：免检索的常驻上下文
- 双层：**static**（长期稳定事实）+ **dynamic**（近期上下文/临时状态）（apps/docs/concepts/user-profiles.mdx:73-91）；第三轴 **buckets** 按主题分桶（preferences/goals/work，分类器自动归桶）（user-profiles.mdx:95-99）。
- 核心论点（user-profiles.mdx:43-69）：语义搜索只返回与 query 相似的内容，而「用户叫 Dhravya」这类事实与任何 query 都不相似——**应该常驻的事实不靠搜索捞**，profile 随每个 prompt 免费搭车，省掉每轮 search 往返。
- MCP 侧落地：`supermemory://profile` resource + `context` prompt，各取 static/dynamic 前 8-12 条拼装（apps/mcp/src/server/resources/profile.ts:10-57，apps/mcp/src/server/prompts/context.ts:12-13）。

### 2.5 MCP server：四档 annotations + 四类工具面
- 16 个工具按**四类 surface** 分类埋点（apps/mcp/src/server/analytics.ts:35-52）：`model_tool`（模型调用）、`app_launcher`（打开交互 UI）、`app_action`（UI 回调）、`app_internal`（UI 内部取数）。
- annotations 四档常量（apps/mcp/src/server/tools/annotations.ts:2-29）：`READ_ONLY`（readOnly+idempotent）、`MEMORY`（destructive，如 add_memory 的 forget 分支）、`ADDITIVE`（非破坏性新增，save-memory）、`SETTINGS`（幂等的会话/账户变更，set-active-tag）。
- server instructions 明确「即使用户不提 supermemory 也要用这些工具」（apps/mcp/src/server/server.ts:28-29）——工具描述里写清触发时机，而非只写功能。
- 工具描述普遍采用「何时用我 / 何时别用我 / 否则用什么」三段式（如 search-memory.ts:24、select-space.ts:14、guided-save.ts:14）。

### 2.6 MCP Apps：工具返回交互 UI
- widget 以 `text/html;profile=mcp-app` MIME 挂成 resource（apps/mcp/src/server/resources/widget.ts:17-38），launcher 工具返回 `ViewMessage`（view/viewId/数据）经 structuredContent + `_meta.ui.resourceUri` 交给宿主渲染（memory-graph.ts:34-54，app-metadata.ts:8-30）。
- 状态放 Durable Object：active space 持久化、上传会话只存 token 的 SHA-256 哈希 + TTL alarm 自动清理（apps/mcp/src/server/space-state.ts:36-72）。

### 2.7 @supermemory/tools：7 个规范工具 + 中间件双路径
- 7 工具：searchMemories / addMemory / getProfile / documentList / documentAdd / documentDelete / memoryForget（skills/supermemory/SKILL.md:146-157）。
- **删除三通道**严格区分（SKILL.md:158-170）：memoryForget 软遗忘单条事实（不删源文档）；documentDelete 硬删源文档（其提取的记忆软遗忘）；用户表述模糊时先 search 再 forget。ID 语义反复强调：`memoryId ≠ documentId`，hybrid 结果里只有含 `memory` 字段的条目才可遗忘。
- 检索三模式 profile/query/full + LRU turn cache（同轮工具循环内免重复 API 调用，packages/tools/src/shared/cache.ts:8-29）+ 归一化去重（memory-client.ts:128-177）。
- Claude 原生 memory tool 适配器：把宿主的 view/create/str_replace/insert/delete/rename 文件命令映射到文档存储，路径归一化为 customId（packages/tools/src/claude-memory.ts:52-150）。

### 2.8 SMFS：记忆挂载为文件系统
- 「Memory your agent can grep」：把 container 挂载成真实目录，agent 用 ls/cat/grep 操作（apps/docs/smfs/overview.mdx:8）。
- 关键设计：**语义 grep 默认**（一次调用全容器语义排序，传任意 flag 则回落真 grep）；memory path 自动蒸馏索引不撑上下文；虚拟 `profile.md` 常驻摘要文件；后台双向同步（smfs/overview.mdx:18-25）。
- 接口哲学：「每个模型都已会文件系统，不用教新 API，语法跨运行时通用」（smfs/overview.mdx:14）。

### 2.9 MemoryBench：开源记忆基准
- 统一管道 INGEST→SEARCH→ANSWER→EVALUATE→REPORT，**每阶段独立 checkpoint 可断点续跑**（apps/docs/memorybench/overview.mdx:39-45）。
- 三个数据集：LoCoMo（多会话事实召回）、LongMemEval（跨会话+中途更新知识）、ConvoMem（个性化/偏好/指代消解）（overview.mdx:59-65）；judge 可插拔防单一评估器偏差。
- 附 Claude Code skill：分析你的记忆代码 → 生成 provider adapter → 跑基准 → 出对比报告（overview.mdx:20-33）。

## 3. 与本仓对照处置表

| # | supermemory 机制 | 本仓现状 | 处置 |
|---|----------------|---------|------|
| 1 | 推断记忆降权 + 审阅队列（isInference 降权，approve/decline/undo）（memory-review.mdx:22-36） | draft/confirm 闸门同构：草稿不进检索语料、confirm 后进、reject_note 驳回（ADR 约定） | **excluded（已有等价，已验证）**：grill 复核确认「declined 即 forgotten」语义完全等价——三个知识服务读路径（默认 BM25 `note_query.py:1030`、check `note_query.py:465`、by_file `note_query.py:672`）全部跳过 deprecated。索引层保留 + `retrieval.py:485` -0.35 降权是刻意设计：① 压出 top-N 槽位区间减少浪费（handler 过滤在 top-N 之后）；② 蒸馏去重召回 `distill_conversation.py:678` 豁免降权，冲突检测需看见已驳回笔记。双层设计自洽，无需改动。undo 回队列本仓无对应通道，但驳回笔记文件仍在磁盘可手工恢复，暂无需求 |
| 2 | Profile 双层 static/dynamic + buckets 主题轴，随 prompt 常驻免检索（user-profiles.mdx:43-99） | get_task_context 注入任务描述+记忆+关联笔记；工作记忆 MEMORY.md（长期）+日记（当日）双层 | **excluded（已有等价）**：双层结构本仓已有。buckets（第三轴按主题分桶）为可选增量，**deferred**——待多任务场景下检索噪声成为实测问题再评估 |
| 3 | Dreaming dynamic/instant：相关文档成组蒸馏 > 孤立单条（graph-memory.mdx:118-126） | capture→distill 批处理（≈dynamic）+ active-settle 停顿点直写（≈instant 语义） | **excluded（已有等价）**：supermemory 的「成组蒸馏质量更高」结论直接验证了本仓 conversation 级 capture + supersede 的设计，无需动作 |
| 4 | Graph 三关系：updates/extends/**derives** + isLatest 时间真值（graph-memory.mdx:67-101） | supersedes（≈updates）+ related（≈extends），无 derives、无时间真值标记 | **deferred**：derives（跨笔记推断新事实）+ isLatest（检索只命中当前真值）是真实缺口，但需要 LLM 推断通道与冲突检测升级，挂知识飞轮主线，不单独立项 |
| 5 | 工具 annotations 四档：READ_ONLY/MEMORY/ADDITIVE/SETTINGS（annotations.ts:2-29） | 无 annotations（memos 调研已裁决挂起搭车，判定标准已定） | **absorbed（维持挂起）**：supermemory 的 ADDITIVE 档（新增非破坏）为本仓「confirm_note/ingest_note 不标 destructive」的裁决提供第二个独立佐证；四档分类可在搭车落地时直接采用 |
| 6 | MCP Apps：HTML resource + ViewMessage + launcher/action 双面工具（widget.ts、app-metadata.ts） | stdio 传输，无 HTTP 宿主 | **excluded**：前提不成立。但「同一工具目录按 surface 分类（model_tool/app_action/app_internal）」的思路，对本仓未来若做 HTTP 传输时的工具分层有参考价值，记入 #5 搭车笔记即可 |
| 7 | SMFS：记忆挂载为文件系统，语义 grep 默认 + 虚拟 profile.md（smfs/overview.mdx:14-25） | 「Cli能力」任务进行中；当前检索面是 MCP 工具 | **deferred→参考**：归「Cli能力」任务。两个可直接借鉴的点：①「agent 已会 ls/cat/grep，别教新 API」的接口哲学——CLI 子命令应对齐 POSIX 心智而非自造语法；②虚拟摘要文件（profile.md ≈ 每目录常驻 README 式摘要，cat 一次拿到全局图景） |
| 8 | MemoryBench：统一基准评记忆系统，checkpoint 管道 + 可插拔 judge（memorybench/overview.mdx:39-67） | 无 LLM 级评估；memos 调研 #4 已 deferred 并入质量量化主线 | **deferred（合流）**：同根信号第三次出现（memos 任务级 eval、llm-wiki-compiler 评分线、MemoryBench）。质量量化主线立项时优先参考其 checkpoint 断点续跑与 judge 可插拔设计；其 Claude Code skill「分析代码→生成 adapter→跑基准」的自动化路径也可复用 |
| 9 | Claude memory tool 适配器：宿主原生记忆命令 → 后端存储映射（claude-memory.ts:52-150） | 本仓自身就是记忆后端（MCP 工具面被宿主调用） | **excluded**：方向相反——supermemory 适配宿主，本仓被宿主适配。但「宿主习惯的接口形状 → 稳定内部 ID」的归一化映射（路径→customId）思路，若本仓未来对接 IDE 原生记忆接口可回看 |
| 10 | 检索 LRU turn cache + 三模式 + 归一化去重（cache.ts、memory-client.ts:128-177） | cache.py 检索缓存 + query_wiki mode 分层（overview/check/全文） | **excluded（已有等价）** |
| 11 | PostHog 工具级遥测：surface/outcome/duration/client 全量埋点（analytics.ts:15-23） | 采纳计数（referenced-docs）+ lint low_adoption 检查 | **excluded（已有等价）**：本仓「采纳计数」比「执行计数」更接近质量信号，方向更优 |
| 12 | SKILL.md 主动推荐技能：「When to Use」+ 何时主动想起用记忆（skills/supermemory/SKILL.md:10-19, 255-257） | 「技能提取」任务进行中 | **参考**：归「技能提取」任务——其 SKILL.md 是现成范本：前置触发场景清单（proactively suggest when...）+ 集成模式对比表（tools vs middleware 选一）+ 删除操作的三通道决策表，信息密度和「教 agent 何时用」的写法都值得模仿 |

## 4. 结论

supermemory 与 memos 是两种截然不同的调研样本：memos 的价值在**协议合规工程**（annotations 推导、structuredContent 规范化），supermemory 的价值在**记忆产品概念**——而后者与本仓的知识飞轮高度同构，多处是不谋而合的相互验证：

- **确认闸门同构**：其「推断记忆降权 + 审阅队列」与本仓「draft → confirm」是同一设计（#1），且其「declined 即 forgotten」的干净语义值得本仓对照自查 reject 后的检索可见性。
- **双层常驻上下文同构**：static/dynamic profile ≈ MEMORY.md + 任务记忆（#2）；「成组蒸馏 > 孤立单条」验证 conversation 级 capture（#3）。
- **annotations 第二佐证**：四档分类中 ADDITIVE 档独立支持了本仓已定的「新增不标 destructive」裁决（#5）。

真正的新增量集中在三处，全部**deferred 归线**而非立即动手：
1. **derives 推断关系 + isLatest 时间真值**（#4）——图谱表达力的真实缺口，挂知识飞轮主线；
2. **SMFS 文件系统接口哲学**（#7）——归「Cli能力」任务，「别教 agent 新 API」+ 虚拟摘要文件两点可直接参考；
3. **MemoryBench 基准框架**（#8）——质量量化主线第三次收到同根信号，立项时优先参考。

再次验证「借鉴调研先证伪」：一个 16 工具的商业记忆产品，12 项候选里 6 项因「已有等价」excluded、2 项方向相反 excluded，真正可动的只有挂线的 3 项 + 2 项归任务参考。**同构验证本身也是调研收益**——它说明本仓知识飞轮的核心设计（确认闸门、双层记忆、成组蒸馏）与商业头部产品的演化方向一致。

## 附：基线

- 仓库：https://github.com/supermemoryai/supermemory
- 基线：HEAD 57b430b（2026-09-18），archive tag `archive/web-2026-09-13-g57b430b`，下次增量调研以此为基线。
- 本地克隆：D:\repos\supermemory
- 关联调研：`docs/memos-调研与借鉴分析.md`（MCP 协议合规工程）、`docs/cognee-调研与借鉴分析.md`
