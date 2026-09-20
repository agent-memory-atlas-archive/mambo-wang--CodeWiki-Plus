# mem0（mem0ai/mem0）调研笔记

> 调研对象：本地克隆 `%TEMP%\mem0-research`（Python OSS SDK，main 分支，2026-09 快照）。
> 所有论断均基于源码核对，标注 `文件:行号`（相对仓库根）。
> 定位对照：mem0 是**用户/Agent 级情景记忆层**（短事实、高 churn、自动增删改），CodeWiki 是**仓库级知识库**（策展笔记、确认闸门）——机制可借鉴，产品形态不同。

## 1. 整体架构与定位

mem0 三位一体：OSS Python SDK（`mem0/`）、TS SDK（`mem0-ts/`）、托管平台（api.mem0.ai，`mem0/client/` 走 REST）。核心引擎在 `mem0/memory/main.py`（约 3700 行，`Memory` + `AsyncMemory` 双类，async 版用 `asyncio.to_thread` 全镜像）。

可插拔工厂三件套：`vector_stores/`（28 个后端：qdrant/chroma/pgvector…）、`embeddings/`（15 个）、`llms/`（21 个），外加 `reranker/`。辅助存储是 **SQLite**（`mem0/memory/storage.py`）：一张 history 表记录每次 ADD/UPDATE/DELETE 的前后值，一张 messages 表存原始对话。

## 2. add() 写入管线（V3 分阶段批处理，核心机制）

`_add_to_vector_store`（`mem0/memory/main.py:916-1084`），`infer=True` 时：

- **Phase 0 上下文收集**：从 SQLite 取该 scope 最近 10 条历史消息喂给 LLM（`main.py:919-921`）；
- **Phase 1 存量检索**：把新消息整体 embed，向量检索 top 10 相似记忆（`main.py:924-931`）；
- **UUID→整数映射（反幻觉关键设计）**：检索结果不把 UUID 给模型，而是映射成 `"0","1","2"...`（`main.py:933-938`），LLM 输出的 UPDATE/DELETE 事件只能引用这些整数 ID，落库前再映射回 UUID——模型**无法幻觉出不存在的记忆 ID**；
- **Phase 2 单次 LLM 调用**：`ADDITIVE_EXTRACTION_PROMPT`（`main.py:942-962`）一次调用输出事件列表 `[{event: ADD|UPDATE|DELETE|NONE, text, id?}]`，agent scope 时追加 `AGENT_CONTEXT_SUFFIX`；LLM 失败显式抛 `LLMError` 而非静默返回空（`main.py:963-969`，注释明确说旧版静默 `return []` 让上游无法区分"LLM 挂了"和"没提取到事实"）；
- **Phase 3 批量 embed**，失败降级逐条（`main.py:991-1003`）；
- **Phase 4/5 MD5 哈希去重**：payload 里存 `hash` 字段，先对 Phase 1 检索结果的哈希集合去重，再对批内去重（`main.py:1005-1024`）——纯确定性去重，不花 LLM；
- **Phase 6 批量落库**：向量批量 insert + 批量写 history，均带逐条降级（`main.py:1045-1084`）；
- **Phase 7 实体链接**：`_link_entities_for_memory`（`main.py:707-728`）从记忆文本抽实体，upsert 进实体存储并回链 memory_id，**全程 non-fatal**。

记忆类型分三种：标准（infer 推断）、非结构化（`infer=False` 逐消息直存，`main.py:879-914`）、程序性记忆（`memory_type="procedural_memory"`，要求 agent_id，LLM 总结后整体存一条，`main.py:2029-2036`；传其他 memory_type 直接校验拒绝，`main.py:831-837`）。

## 3. search() 检索：三信号混合打分

`_search_vector_store`（`mem0/memory/main.py:1628-1668`）+ `score_and_rank`（`mem0/utils/scoring.py:60-119`）：

1. **语义**：query embed，向量检索，**过采样 4 倍**（`internal_limit = max(limit*4, 60)`）做候选池；
2. **关键词 BM25**：写入时预计算 `text_lemmatized`（词形还原）存 payload，查询时同样 lemmatize 后走 `keyword_search`，BM25 原始分用 sigmoid 归一化（`main.py:1646-1659`）；
3. **实体加权**：查询抽实体（去重最多 8 个），批量 embed 后搜实体库（阈值 ≥0.5），命中实体回链的记忆获得 boost，上限 0.5、权重 0.5（`main.py:1733-1763`、`scoring.py:57`）；
4. **融合**：`combined = (semantic + bm25 + entity_boost) / max_possible`，除数按活跃信号自适应；**语义分先过 threshold 门槛再融合**——BM25/实体只能提排序，救不回语义不及格的候选（`scoring.py:74-119`）；
5. 可选 rerank、`explain=True` 输出各信号分值明细。

scope 强制：`search`/`get_all` 必须带 `filters={user_id|agent_id|run_id}` 至少之一，否则 ValueError（`main.py:1303-1307`）；顶层实体参数被显式拒绝，强制走 filters（`main.py:1282`）。payload 里还有 `expiration_date`，读取时默认过滤过期记忆（`main.py:1355`）。

## 4. 图记忆的进与退（重要信号）

mem0 曾内置 Neo4j/Memgraph/Kuzu/Apache AGE/Neptune 图存储驱动，**2025 年整体删除**（约 4000 行，PR #4805，`docs/changelog/sdk.mdx:368`），改为上文的原生实体链接 + 查询期实体 boost。教训：**重图数据库依赖换来的关系推理收益，不如"实体抽取 + 倒排回链 + 检索期加权"的轻量方案**——CodeWiki 的 `ontology.yaml` 路线与此结论一致，不必引入图库。

## 5. 外围机制

- **OpenAI 兼容代理**（`mem0/proxy/main.py:47-161`）：`chat.completions.create` 透明拦截——后台 daemon 线程异步 `add()` 写记忆（不阻塞响应），同步 `search()` 取相关记忆注入最后一条 user message。应用零改造获得记忆能力；
- **历史账本**：每次变更写 SQLite history（prev_value/new_value/event/actor_id/role/is_deleted，`main.py:2080-2089, 2112-2122`），UPDATE 时实体链接先摘除旧文本实体再重链新文本（`main.py:2091-2096`）；
- **通知/远程配置**（`mem0/memory/notices.py:22-97`）：从 GitHub raw 拉运营文案 JSON，1h TTL 缓存，拉不到用随包 bundled 兜底；按 SHA1 哈希分桶做 displayed/holdout 变体对照，且带用量上限（7 天窗口最多 10 次）防骚扰；
- **Agent Skills 分发**（`skills/`）：随包带 6 个 SKILL.md（mem0、mem0-cli、mem0-integrate…），frontmatter 写明 TRIGGER/DO-NOT-TRIGGER 条件，skill 之间互链成 graph（`skills/mem0/SKILL.md:1-31`），把"装进 Claude Code/Cursor"做成一等分发渠道；
- **遥测**：`capture_event` 贯穿所有 API，PostHog 特性开关驱动功能灰度。

## 6. 值得 CodeWiki 借鉴的点

按落地难度排序，均映射到 CodeWiki 现有组件：

1. **整数 ID 反幻觉映射**（借鉴成本：低，收益：高）→ `distill_conversation` / `consolidate_notes` 的 UPDATE/MERGE 路径。凡是要 LLM 引用既有笔记做合并/更新的场景，prepare 阶段把候选笔记的稳定 ID 映射成 `"0","1","2"`，submit 时校验整数范围并映射回真实 ID，映射外的引用直接拒绝。比"提示词里求模型别编 ID"可靠一个数量级（`main.py:933-938`）。
2. **单次调用输出事件流**（低，高）→ 蒸馏 submit 协议。mem0 一次 LLM 调用同时产出 ADD/UPDATE/DELETE/NONE 四类事件，而不是"先提取再逐条判重"。CodeWiki 蒸馏的 notes 输出可增加 `event` 字段，让"新事实覆盖旧笔记"在蒸馏期一次完成，省掉事后 consolidate 的判重调用（`main.py:940-984`）。
3. **MD5 哈希前置去重**（极低，中）→ 笔记入库前算正文哈希存 frontmatter，`ingest_note`/`confirm_note` 先查哈希集合，纯确定性去重零 LLM 成本，语义去重留给 LLM 只处理"改写不同但意思相同"的部分（`main.py:1005-1024`）。
4. **混合打分 + explain 模式**（中，高）→ `query_wiki` 排序。当前是采纳权重（2x）单一信号；可加 BM25 关键词信号（笔记正文写入时预计算 lemmatized 副本）+ "语义分先过门槛再融合"的门控模式，并加 `explain` 参数输出各信号分值——既提升命中率又让调优可观测（符合 Doctrine"归因调优先实测计数"）。过采样 4 倍再 rank down 的候选池模式也直接可用（`scoring.py:60-119`、`main.py:1640-1644`）。
5. **变更历史账本**（中，中）→ 笔记存储层。CodeWiki 笔记有 status 但无历史；加一张 SQLite history 表（note_id/prev_content/new_content/event/actor/timestamp），`confirm_note`/`reject_note`/更新时落一条，为将来做审计、回滚、"这条结论改过几次"提供地基（`main.py:2080-2089`）。
6. **实体轻量图替代重图库**（已对齐，可强化）→ mem0 用 4000 行删除验证了 CodeWiki `ontology.yaml` + 检索期实体 boost 的路线是对的；可进一步借鉴其"实体→笔记回链表 + 查询期 boost ≤0.5"的具体参数（`main.py:1733-1763`）。
7. **Skill 分发渠道**（低，中）→ 把 CodeWiki 的 MCP prompts（task-workflow、distill-conversations 等）包装成标准 SKILL.md 随包分发，frontmatter 写清 TRIGGER 条件，抢占"装进宿主 Agent"的入口。mem0 的 skill graph 互链模式（每个 skill 声明兄弟 skill 的分工边界）值得照抄（`skills/mem0/SKILL.md:26-31`）。
8. **运营文案 fail-open**（低，低）→ 远程配置拉取失败用 bundled 兜底 + TTL 缓存 + 用量上限，与现有 Doctrine"注入/采集类代码 fail-open"完全同构，可作为实现参照（`notices.py:62-87`）。

**明确不借鉴**：mem0 的自动 UPDATE/DELETE 无确认闸门（`add()` 一次 LLM 调用直接改写/删除存量记忆）——它赌的是"事实低价值、错了能靠 history 找回"，CodeWiki 的知识是决策依据，确认闸门（draft→confirm）必须保留；mem0 用 history 账本补偿无闸门的风险，恰好反证了闸门+账本应该配套。

## 7. Agent 宿主 Hook 插件体系（integrations/）

三层抓取机制：SDK 显式调用、OpenAI 兼容代理（monkey-patch，`proxy/main.py:100-105`）、**宿主 Hook 插件**（15 个宿主：claude-code/cursor/codex/opencode/kimi 等，共享 `agent-plugin-core` 内核）。

以 Cursor 为例注册 8 个生命周期事件（`integrations/cursor-plugin/hooks/hooks.json:4-11`）：`sessionStart`（恢复 pending）、`beforeSubmitPrompt`（**首 prompt 检索记忆注入**，`hookSpecificOutput.additionalContext`，top_k=5、2s 超时，`hook_runner.py:62-94`）、`postToolUse`/`postToolUseFailure`（记录工具调用）、`stop`/`afterAgentResponse`（记录回复）、`preCompact`/`sessionEnd`（触发 flush）。

关键工程设计（`integrations/agent-plugin-core/python/hook_runner.py`）：

- **hook/worker 解耦**：hook 只写 `pending/*.json` handoff 文件，`subprocess.Popen` 拉起 detached flush worker 异步上传（`_launch_handoff`，`hook_runner.py:97-128`），hook 毫秒级返回；
- **崩溃恢复**：`.running` 超 300s 视为 stale 重新排队，pending 包 7 天过期，session-start 最多恢复 5 个（`recover_pending_handoffs`，`hook_runner.py:131-155`）；
- **三种 flush 触发**：session-end（默认）、periodic checkpoint（按条数阈值）、idle（默认 300s）；
- **fail-open**：解析失败返回 `{}`、异常只写日志、入口永不非零退出（`hook_runner.py:352-359`）；
- **可暂停**：`pause` skill 停采集，pending 保留。

**对 CodeWiki 的借鉴评估**（对照 `codewiki/hooks/capture_session_end.py`）：轻量 hook + 重活外移 + fail-open 两者已同构，CodeWiki 甚至语义更严谨（"成功只代表采集已启动"）。三个增量机制中：pending 恢复解决的是云端上传不可靠（CodeWiki 本地写文件无此问题，低价值）；首 prompt 检索注入依赖纯向量检索（CodeWiki hook 无 LLM 做不了检索词推导，且任务记忆链路已由 SessionStart 注入 + `get_task_context` 覆盖，仅"按需注入 top-3 笔记标题"思想可留）；**idle/periodic checkpoint 对应 CodeWiki 真实痛点（长会话崩溃丢对话），但 CodeBuddy 的 Stop/PreCompact 事件不携带 transcript_path，已试过并回撤（2026-09-16 笔记），属宿主能力限制**——若 IDE 将来补上 transcript 增量，mem0 的 `checkpoint_due` 阈值模式是现成模板。

## 8. 明显短板/局限

1. **无确认闸门**：LLM 单次调用即可改写/删除既有记忆，错误合并不可逆（只有 history 可查，无恢复 API 暴露给用户）；
2. **主文件过重**：`main.py` 3700 行，sync/async 全镜像导致每个改动双份维护；
3. **scope 模型偏窄**：只有 user_id/agent_id/run_id 三维，无组织/项目层级，多租户要靠平台版；
4. **实体链接 non-fatal 吞错**：链接失败只 debug 日志，实体库与记忆库可能静默漂移（`main.py:725-728`）；
5. **代理层异步写用 daemon 线程**：进程退出可能丢写入（`proxy/main.py:149-161`）。

## 一句话总结

mem0 的核心工程智慧是"**用确定性簿记包裹 LLM 不确定性**"：整数 ID 映射防幻觉、MD5 哈希防重复、语义门槛门控融合、history 账本兜底自动变更、删图库走轻实体链接——每一层都在收窄 LLM 的自由度；CodeWiki 可直接吸收其 ID 映射、事件流蒸馏协议、混合打分与历史账本四个机制，同时反其道保留确认闸门。
