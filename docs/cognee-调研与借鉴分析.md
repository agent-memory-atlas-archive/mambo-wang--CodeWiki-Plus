# cognee 调研与借鉴分析

> 调研对象：[topoteretes/cognee](https://github.com/topoteretes/cognee)（本地克隆 `D:\repos\cognee`，HEAD `c0d18c80e`，v1.5.4，2026-09-09）
> 调研日期：2026-09-18 · 关联任务：他山之石

## 一、项目定位

cognee 是「AI Agent 记忆引擎」，主打 "Memory for AI Agents in 60 seconds"。核心范式是 **ECL（Extract-Cognify-Load）**：`add()` 摄取 → `cognify()` 建知识图谱 → `search()` 检索。在标准 ECL 之上，v1.5.x 围绕「会话记忆闭环」长出了一整套与 CodeWiki 知识飞轮高度同构的机制：会话缓存（SessionManager）、会话蒸馏（session_distillation）、反馈加权（feedback weights）、Agent 轨迹提取（agent trace）、编码规则提取（codingagents）。

顶层 API 面（`cognee/api/v1/`）：`add` / `cognify` / `search` / `memify`（图谱增强）/ `improve`（会话桥接+增强）/ `remember` / `forget`。另有 `cognee-mcp` MCP 服务端与 Claude Code 插件（`improve.py:522-525` 提到 "the Claude Code plugin's tool-call activity"）。

## 二、工作机制（重点：与 CodeWiki 知识飞轮对照）

### 1. memify：图谱增强流水线（`cognee/modules/memify/memify.py:27`）

对已建好的图跑增强任务，不传 data 时直接把整个图（或子图）作为输入。任务可用 **字符串名或 Task 实例** 混合传入，由注册表解析（`memify_pipelines/memify_task_registry.py:71` `resolve_memify_tasks`）：未知名字抛 `CogneeValidationError`（HTTP 422），需要调用级参数的任务（如 `extract_feedback_qas` 要求 `session_ids`）只留 SDK 通道、不进注册表。默认流水线：`extract_subgraph → extract_subgraph_chunks → get_triplet_datapoints → index_data_points`（三元组嵌入索引）。

### 2. improve：会话→永久图谱的桥接总入口（`cognee/api/v1/improve/improve.py:39`）

传 `session_ids` 时按序跑 7 个 stage，**每个 stage 独立 fail-open**（一个失败只打 warning，不阻塞其余）：

| Stage | 机制 | 关键代码 |
|---|---|---|
| 1 反馈加权 | 见下 | `tasks/memify/apply_feedback_weights.py:212` |
| 2 持久化会话 Q&A | 水位线增量，见下 | `tasks/memify/extract_user_sessions.py:16` + `cognify_session.py:19` |
| 2b 持久化 Agent 轨迹 | Claude Code 插件的工具调用步骤（每会话数百条 Bash/Edit/Read/Write）cognify 进 `agent_trace_feedbacks` 节点集 | `improve.py:514` |
| 2b2 Agent 上下文提取 | LIVE 确定性 + BATCH LLM 两级，见下 | `infrastructure/session/agent_context_extraction.py:1` |
| 2c 会话蒸馏 | curator 分批 → 逐条 writer/rejecter，见下 | `modules/session_distillation/distill.py:1` |
| 2c2 用户偏好 | 评分轮次加权 `prefers` 边、闲置衰减、中性剪枝 | `improve.py:470` |
| 2d 真值子空间 | opt-in 默认关；session_learnings 嵌入重放为 K 个质心槽，chunk 投影打分 | `modules/truth_subspace/build.py:108` |
| 3 默认增强 | memify 三元组嵌入 | `improve.py:266` |
| 4 全局上下文索引 | opt-in；对图上 TextSummary 做分桶摘要（graph/vector 两种分桶策略，max_bucket_size=4） | `tasks/memify/global_context_index/update.py` |

**并发防护**：单会话 improve 用 `try_acquire_improve_lock` 串行化（`improve.py:174-187`）——auto-improve、idle-watcher、SessionEnd 三个触发源不会重复干活；抢不到锁直接返回 `{}` 而非排队。

### 3. 反馈加权：流式更新公式（`apply_feedback_weights.py:43-59`）

- 评分 1..5 归一化到 0..1：`(score-1)/4`；
- 流式更新：`w_new = w_old + α·(rating − w_old)`，α 默认 0.1，裁剪到 [0,1] 保留 4 位小数；
- **只动检索时真正用到的元素**：每条 Q&A 记录 `used_graph_element_ids`（node_ids/edge_ids），无检索记录则零更新；
- 幂等标记：每条 Q&A 的 `memify_metadata` 里记 `feedback_weights_applied: true`，重跑跳过（`apply_feedback_weights.py:152-156`）；且 update_qa 是 overlay 合并，只传本 stage 的 key，防止把别的 stage 的旧值覆盖新值（`:123-126` 注释）；
- 频率权重独立通道：每次被检索用到 +1.0（`apply_frequency_weights.py:84`），与反馈权重分开存取。

检索侧消费：`get_memory_fragment` 投影图时把 `feedback_weight` 带上，配合 `triplet_distance_penalty=6.5`、`feedback_influence` 参与排序（`modules/retrieval/utils/brute_force_triplet_search.py:50-74`）。

### 4. 会话持久化水位线（`infrastructure/session/session_persist_watermark.py:1-19`）

模块 docstring 直说这是修 O(n²) 的：旧实现每次 improve 都把**整个会话**重新 add/embed/抽取成新文档。改为按 (user, session) 存一个计数水位线（内部非渲染的 session-context 行）：

- 抽取时只取水位线以上的新条目，打包成一个 `SessionPersistWindow`（含抽取时刻的总条数）；
- `cognify_session` 成功后才推进水位线；失败则水位线不动，下次 improve 重试同一窗口（add 层内容哈希去重保证重试安全，`cognify_session.py:70-86`）；
- **陈旧水位线检测**：水位线 > 当前条数说明会话被清空重建，视为过期、从头持久化（`extract_user_sessions.py:71-82`）。

### 5. Agent 轨迹两级提取（`agent_context_extraction.py:1-17`）

- **LIVE（零 LLM）**：每条轨迹落库后，errored step 直接从错误文本构造 `failure_lessons` 候选，置信度 0.85（硬编码，注释说明"错误是强信号，轻松过 0.75 的门"）；
- **BATCH（LLM）**：每 10 条轨迹触发一次（`TRACE_EXTRACTION_INTERVAL=10`，重叠 3 条保序列上下文），在轨迹写入路径内联 await——跨过间隔的那次写入要付一次 LLM 延迟；improve/会话结束时再冲刷尾部；
- 两条路径汇入同一个确定性 applier（置信门控 + 去重），QA lessons 与 trace lessons 同一套规则；
- **fail-open 铁律**：提取永不向轨迹写入路径抛异常，失败只是这次没学到；
- **脱敏先行**：错误文本入库前正则抹除 Bearer/JWT/api_key/secret/32+位hex/UUID/长数字（`:62-93`）。

### 6. 会话蒸馏（`modules/session_distillation/distill.py:1-11`）

四步：LOAD（QA 轮次 + 可蒸馏的 gated 上下文条目）→ CURATE（时间线打包成批，每批一次 curator LLM 调用，并发受限）→ ACCEPT（**逐条** lesson：先在 `session_learnings` 节点集内做 novelty 检索，再 writer/rejecter LLM 裁决，实体锚定）→ PERSIST（接受的 lesson 渲染成文档，一次 add+cognify）。单元级 fail-open：一个批次失败只丢自己的活。

### 7. 单次 LLM 调用多产出（`infrastructure/session/feedback_detection.py:46-63`）

turn 分析一次调用同时产出：答案路由、对**上一轮实际服务的上下文条目**的评分（`served_context_ratings`）、候选上下文更新——把 served context 以 `id: content` 块拼进输入即可，零额外调用。LLM 失败/超时返回空分析，主流程永不阻塞。

### 8. codingagents：编码规则提取（`tasks/codingagents/README.md`）

从 AGENTS.md/对话/commit message 用 LLM 结构化抽取 `Rule` 节点，并建 `rule_associated_from` 边回链到来源 `DocumentChunk`。**memify 默认自动跑**，cognify 默认不跑。

## 三、值得 CodeWiki 借鉴的

| # | 借鉴点 | cognee 依据 | CodeWiki 现状与落点 |
|---|---|---|---|
| 1 | **水位线增量持久化 + 失败不推进 + 陈旧检测** | `session_persist_watermark.py`：只处理新增量，成功才推进，会话缩短视为水位线过期从头来 | CodeWiki 蒸馏靠 pending raw 清单轮询。任务记忆/多仓工作区若出现「周期性全量重算」场景（如 Doctrine 刷新、index 重建），应套用同款水位线三件套，避免 O(n²) |
| 2 | **LIVE 确定性 + BATCH LLM 两级提取** | 错误轨迹零成本即时成 lesson（置信 0.85），每 10 条才付一次 LLM；两路汇入同一确定性 applier | CodeWiki hook 采集目前只落 raw 不做任何即时提取。可在 capture 侧加零 LLM 的确定性快路径（如识别到报错堆栈/用户否定词直接标记 raw 高优先级），蒸馏 subagent 只处理需要推理的部分 |
| 3 | **脱敏先行，错误文本入库前正则抹除** | `agent_context_extraction.py:62-93`：Bearer/JWT/secret/UUID/长数字全抹 | `capture_conversation` 落 raw 前应加同款确定性脱敏——raw 是要长期留存并喂给 LLM 的， secrets 进了 raw 就晚了 |
| 4 | **单次 LLM 调用多产出** | turn 分析一次调用出路由+条目评分+候选更新 | CodeWiki 蒸馏 submit 已是单次提交，但「确认草稿时顺便产出 adoption/冲突信号」这类同上下文多产出可参考，减少对同一内容的重复 LLM 调用 |
| 5 | **流式加权公式替代裸计数** | `w += α(r−w)`，α=0.1，裁剪 [0,1]；频率与反馈双通道分开存 | CodeWiki 的 adoption 计数是裸累加，老笔记权威值只增不减。借鉴流式更新让「近期零采纳」能自然衰减权威值，且反馈（显式确认/拒绝）与频率（被检索次数）分通道，语义不混 |
| 6 | **幂等标记 + overlay 合并写** | 每条 Q&A 的 `memify_metadata` 记各 stage 处理结果；update 只传本 stage 的 key 防 stale 覆盖 | CodeWiki 的 supersede/近重复拒绝已有类似语义；「多写方并发更新同一条目时只传增量 key」的 overlay 纪律值得写进任务记忆存储层的约定 |
| 7 | **单会话锁防多触发源重复干活** | `try_acquire_improve_lock`：抢不到直接返回空，不排队 | CodeWiki 补蒸馏 subagent 若与主动沉淀并发写同一任务记忆，应有同款「抢锁失败即放弃」而非双写 |
| 8 | **novelty 检索限定在同类节点集** | 蒸馏 lesson 的查重只搜 `session_learnings` 节点集，不搜全图 | CodeWiki `ingest_note` 前的 `query_wiki` 查重可加 note_type/来源范围过滤，减少跨类型误判 related≠same |

## 四、不建议借鉴的

- **图数据库 + 向量库全家桶**：cognee 的加权、投影、三元组检索全部建立在 Neo4j/Kuzu + 向量引擎之上；CodeWiki 是零依赖单机 Markdown + BM25（ADR-0001），引入图库违背轻量哲学。要借的是**语义**（权重衰减、水位线），不是**底座**。
- **自动反馈加权（无确认闸门）**：cognee 每次检索用到的元素权重被静默修改，与 CodeWiki「入库必经显式确认闸门」核心原则冲突。若引入权威值衰减，衰减规则必须确定性、可解释、lint 可审计，不能由单次交互静默改写。
- **truth subspace 质心槽**：实验性 opt-in 特性，把 lesson 嵌入重放成 K 个质心再投影打分，对 Markdown 规模的知识库收益存疑，且依赖向量底座。
- **全局上下文索引分桶摘要**：每次 build 对全图 TextSummary 做 LLM 分桶归并，成本高，且自动生成聚合内容绕过确认闸门——与 graphiti 调研中「自动社区摘要」的否决理由相同（依据：docs/graphiti-调研与借鉴分析.md 第四节）。
- **LIVE 提取内联在写入路径**：BATCH 每 10 条在 trace 写入路径内联 await 一次 LLM，写入方要付延迟。CodeWiki 的 hook 采集必须保持零阻塞（fail-open、永不非零退出），即时提取若需要 LLM 一律后台化。

## 五、一句话总结

cognee 与 CodeWiki 是同一命题（会话→持久知识闭环）的两种底座实现：它验证了**水位线增量、确定性快路径+LLM 慢路径、脱敏先行、流式加权**这四个底座无关的工程习惯的价值——这四条全部可以平移进 CodeWiki 的采集/蒸馏/权威值体系；而它的图库底座、自动静默加权和实验性质心机制，在 Markdown 单机哲学下应明确不借。
