# hindsight 调研与借鉴分析

> 调研日期：2026-09-19 · 任务：他山之石 · 方法：克隆源码读代码（D:\repos\hindsight，HEAD 0a58d69，2026-09-19 当日提交，约 4740 文件），结论均经代码核对，非文档站口径。

## 1. 项目概况

| 维度 | 事实 |
|------|------|
| 定位 | vectorize.io 出品的「生物拟态」AI Agent 长期记忆系统（hindsight-api 服务 + 多语言 SDK + coding-agents 集成包），云端为主、可自托管/本地 daemon |
| 形态 | `hindsight-api-slim/`（Python FastAPI 引擎，engine 目录 158 个 py 文件，memory_engine.py 单文件 1.1MB）+ `hindsight-integrations/coding-agents/`（TypeScript，一个包接 18 个编码 Agent）+ `skills/hindsight-docs/`（154 篇参考文档打包成 Agent skill） |
| 核心抽象 | Memory Bank（隔离存储单元）× 三操作：retain（摄入提取）/ recall（检索）/ reflect（推理综合） |
| 记忆分层 | fact（world/experience/observation 三型）→ observation（证据合并的信念）→ mental model / knowledge page（预计算的综合文档） |
| 活跃度 | HEAD 为调研当日提交，迭代极快（README 记录的 issue 修复如 #3506 均为近期） |
| 成本模型 | 每次 retain 都跑 LLM 提取，consolidation、page refresh 又是独立 LLM 调用——**重 LLM、重基建**（Postgres + embedding + cross-encoder），与本仓「工具无状态、LLM 外置」相反 |

领域上 hindsight 是通用记忆服务、本仓是代码知识库，但 coding-agents 集成层解决的问题与本仓几乎同构：**如何把项目历史（git + 对话）变成 Agent 开工前就能看到的知识，并让 Agent 主动检索而非被动喂**。该层是本次调研的主要收获来源。

## 2. 核心机制（代码核对）

### 2.1 记忆管线：retain → consolidation → observations
- retain 时 LLM 提取 facts/entities/relationships，**原文永不逐字存储**（skills/hindsight-docs/references/best-practices.md:36）。fact 分三型：`world`（外部事实）/ `experience`（用户事件）/ `observation`（多证据合并的信念，带 proof_count）（best-practices.md:46-53）。
- consolidation 在 retain 之后自动跑：把新 facts 与既有 observations 一起交给 LLM，产出 `creates/updates/deletes` 三个数组，**每条必带 reason**（hindsight-api-slim/hindsight_api/engine/consolidation/prompts.py:111）。
- 合并规则九条，关键的几条：**PREFER UPDATE OVER CREATE**——同一 canonical 事件/决策/模式绝不建近重复兄弟（prompts.py:39）；**一 observation 一 facet**（prompts.py:41）；**按实体/facet 匹配而非按主题**（prompts.py:43）；状态变化**级联**到所有受影响 observations（prompts.py:47）；**NO COMPUTATION**——"user 说卖了 X"绝不递减计数，只记录明说的数字（prompts.py:53）；重大历史事件**永不删除**（prompts.py:51）。
- **Mission 优先级**：bank 的 mission 与 PROCESSING RULES 冲突时 mission 赢（prompts.py:19-22）——把「领域定制」放在数据（mission）而非代码（规则）里。
- **语言保持规则**：每条 observation 用其自身源事实的语言写，混语言合并时多数胜出，且禁止在旧句子上"焊"新语言细节，必须用新语言重写整句（prompts.py:31-35）——注释明言这是防多语模型漂移的管线级默认。

### 2.2 Knowledge pages：delta 刷新的活文档
- page 只是 `knowledge_pages` 树节点，内容存在其引用的 mental model 里（memory_engine.py:18892-18894）——**结构与内容分离**。
- 默认 trigger：`mode: "delta"`（增量编辑而非重建）、`fact_types: ["observation"]`（只吃合并后的信念层，不吃原始 facts）、`exclude_mental_models: true`（页与页互不引用，防自反）（memory_engine.py:18901-18906）。
- trigger 是**字段级 merge 而非整体替换**：客户端只设一个字段不再静默丢掉其余默认值；`refresh_cron` 与 `refresh_after_consolidation` 互斥，同设即拒（memory_engine.py:18908-18949）。注释记录了两个真实 bug（#3506 及其 PATCH 路径残留）——全量替换语义在「API 层会填默认值」的场景下必然踩坑。
- coding-agents 给每个 repo 播种**五页固定分类法**，每页钉死一个知识层 tag，只从对应层的事实合成：Component map（`knowledge:component`）、Core concepts（`knowledge:concept`）、Conventions and patterns（`knowledge:convention`）、Key decisions and rationale（`knowledge:decision`）、Initiatives and enhancements（`knowledge:feature-work`）（hindsight-integrations/coding-agents/README.md:607-613）。
- 刷新错峰用 Jenkins 式 `H` 语法：`"H * * * *"` 让每页按 bank id + 页名哈希到自己的分钟，避免五页 × 每 bank 同一分钟挤爆 worker 池；`H` 在插件侧解析成普通 cron，API 看到的永远是可编辑的普通表达式（README.md:567-589）。

### 2.3 检索：4 臂并行 + RRF 融合
- 四臂：semantic / bm25 / graph / temporal（engine/search/fusion.py:56），融合用 Reciprocal Rank Fusion，`score(d) = Σ 1/(k + rank)`，k=60（fusion.py:29-33）。
- 融合前**每臂截断**（cap_per_source），防一个过度扩张的后端在 reranker 全局候选预算里挤掉其他臂（fusion.py:8-26）。

### 2.4 Reflect、staleness 与 retraction
- mental model = 预计算的 reflect 响应，高频查询即时返回（best-practices.md:40）。
- staleness 判定：上次刷新之后有新的 in-scope 记忆写入即过期，逐 model 计算（engine/reflect/tools.py:210-231）。
- **retraction**：文档记录自己 `based_on` 了哪些 fact id；当某 fact 被失效/删除/清扫，行直接消失，但文档还在引用它。该模块把「缺失」变成值：拿 stored based_on 与存活 id 集合做纯 dict 变换，无 DB 无 LLM 可测；且刻意**不区分失效原因**（invalidated/deleted/re-ingest 从文档视角是同一事件），allowlist 严格限定可查 fact 类型，防误伤健康文档（engine/reflect/retractions.py:1-44）。

### 2.5 coding-agents 集成层（对本仓最有价值的部分）
- **零设置摄入**：SessionStart 钩子做冷启动播种（git 历史 autoSeed + headless codebase survey），UserPromptSubmit 做 recall+注入，Stop 做会话写回（README.md:56, 74, 542-548）。git 摄入三档：`"message"`（仅 commit message，HEAD 移动时 re-upsert）/ `"full"`（含逐 commit diff）/ `"none"`（README.md:552）。
- **每仓一 bank、跨 Agent 共享**：默认 `coding-agent::{gitProject}`，18 个 Agent 共享同一仓的记忆（README.md:249-251, 520）。
- **索引抑制（实测数据）**：注入块刻意**不列知识页清单**，只说「N 页覆盖本仓库，刻意不列出，请调 search」。注释给出实测：对预填充 bank 的 40 个真实 Claude Code 轮次，**每一次检索都是拿注入块里抄来的 id 直接 read——3 页时 0 次搜索，12 页时仍然 0 次**。结论：标题清单读起来像索引，而索引让搜索失去意义（src/core/knowledge-injection.ts:27-47）。
- **when-to-call 工具指南**：注册工具不够，每个工具的**触发时机**必须反复出现在上下文里——SessionStart 前言 + 每 10 轮刷新都重注入工具指南，逐工具写清「什么时刻该伸手」（knowledge-injection.ts:50-83, README.md:537）。
- **引用可见**：用了记忆要用固定格式的 blockquote 显式致谢，「致谢改变你做法的那次搜索，而不只是你引用的那些」（knowledge-injection.ts:68-70）。
- **降级链留痕**：自动注入 `autoInject: "reflect"` 超时或 5xx 时降级为知识页搜索，再降级为裸 recall，且降级被记录（README.md:530, 533）。
- **apiToken 热更新**：长驻 Agent 不重启也能换密钥——每次请求被拒后重读 token（README.md:461-465）。
- **会话归属绝不猜**：导入历史对话时只认 session 自己记录的 cwd，绝不从文件夹名推断——`/` 和 `.` 都编码成 `-`，`repo-sub` 无法区分子目录还是兄弟仓，猜错就把别人的对话归进你的 bank；记录不足的 session 跳过并报数（README.md:338-352）。
- **opt-in 隐私开关 fail-closed**：`optInOnly` 下未批准路径完全惰性；`mapPathToBank` 算批准而裸 `bankId` 不算——「隐私开关必须 fail closed」；**刻意不做 repo 内携带的配置文件**：克隆来的仓库不能自己打开记忆（README.md:472-497）。
- **manageBankConfig 只增不改**：插件给 bank 写 retain 策略/label 组/mission 时严格 additive，用户在控制面的任何编辑永远赢（README.md:527, 725-731）。
- **Memory Defense**：retain 前按策略做敏感信息筛查/脱敏；策略解析**刻意不 try/except**——畸形策略必须让 retain 失败而非静默跳过，「安全控制 fail-open 是错的默认」（engine/retain/orchestrator.py:58-80）。

### 2.6 背压
- retain 管线有字节级内存预算：生产者提取、消费者写库各持预留，批攒到预算一半即 flush，另一半留给生产者继续提取——防「正确但串行化」的停顿（engine/retain/memory_budget.py:114-148）。

## 3. 与本仓对照处置表

| # | hindsight 机制 | 本仓现状（代码核对） | 处置 |
|---|---------------|---------------------|------|
| 1 | 索引抑制：注入块列页清单 → 40 轮实测 0 次搜索，全拿 id 直接 read（knowledge-injection.ts:27-47） | 会话注入的【知识库提示】列 3 条最新笔记标题作新鲜度信号 + 检索指引，未列全量目录 | **absorbed（原则）**：采纳「命名数量与入口，不列内容清单」。现状已部分符合（只列 3 条最新、且检索指引在前）；明确约束：未来任何会话注入不得扩展为全量笔记/文档索引。实测数据存档备查 |
| 2 | 知识页 delta 刷新：增量编辑而非重建 + based_on 事实追踪（memory_engine.py:18901-18906） | wiki 文档 Agent 手写、lint_wiki 查过时；refresh_doctrine 全量重生成 | **deferred**：delta 编辑可省 refresh_doctrine/overview 再生成的 token 并减少内容抖动，但前提是文档能追踪自己引用了哪些笔记（based_on），本仓笔记粒度粗、基建成本高。等 doctrine/overview 再生成成本成为实际痛点再评估 |
| 3 | consolidation prompt 规则：每条 op 必带 reason；NO COMPUTATION（不做算术/逻辑推断，只记明说的）（prompts.py:53, 111） | 知识聚合 SOP 已有 UPDATE>MERGE>CREATE 人工分组；distill/聚合 prompt 无此两条 | **absorbed（已落地）**：经 grill 拷问定案（ADR-0012），两条规则合并为第 6 条纪律写入 `_DISTILL_SYSTEM`（"Reasoned and literal"），聚合侧不动（dispositions 已强制 reason），测试补断言，全量 1169 passed |
| 4 | retraction：based_on id 失活自动撤回文档依据（retractions.py:1-44） | supersedes 显式传参（ADR-0009） | **deferred**：自动失活检测需事实级 id 追踪；本仓 supersedes 显式链已覆盖主场景，等出现「笔记被删但引用它的文档无人察觉」的实际案例再议 |
| 5 | 4 臂检索 + 每臂截断 + RRF 融合（fusion.py:8-60） | query_wiki：jieba 分词 + BM25 + 本体扩展，单臂 | **deferred**：语义臂需 embedding 基建，违背成本可见性原则不暗加；但「多臂各自截断再 RRF」的融合框架值得记住——若未来 query_wiki 加标题/正文/wikilink 多路召回，RRF 是现成融合公式，无需重造 |
| 6 | Mission 优先于处理规则：领域定制放数据不放代码（prompts.py:19-22） | ontology.yaml 本体论模板 + schema.yaml 约定，同思路 | **excluded**：等价——本仓已把领域定制外置到配置 |
| 7 | 语言保持规则：observation 用源事实语言，混语合并多数胜出（prompts.py:31-35） | 语言闸门：所有产出中文 | **excluded**：等价且更严格（本仓统一中文，无混语合并问题） |
| 8 | when-to-call 工具指南反复注入（每 10 轮刷新）（knowledge-injection.ts:50-83） | AGENTS.md 注入工具使用建议（query_wiki 前置、ingest_note 时机等） | **excluded**：等价；「触发时机必须反复在上下文里」的原则本仓已践行 |
| 9 | 引用致谢 blockquote + 致谢改变做法的搜索（knowledge-injection.ts:68-70） | 正文标注（依据：<file>）+ codewiki:referenced-docs 采纳声明 | **excluded**：等价（人读 + 机读双通道本仓更完整） |
| 10 | 降级链留痕：reflect 超时 → 页搜索 → 裸 recall，降级被记录（README.md:530） | fail-open 原则（注入/采集代码永不非零退出） | **excluded**：等价；「降级要留痕」可作 fail-open 实现的细节要求，本仓日志已覆盖 |
| 11 | Memory Defense：retain 前脱敏，策略畸形 fail-closed（retain/orchestrator.py:58-80） | raw 逐字存用户消息，本地 markdown 文件 | **excluded**：本仓本地优先、无多租户无云端，威胁模型不成立 |
| 12 | 每仓一 bank 跨 Agent 共享 / 会话归属只认自记录 cwd / opt-in fail-closed / manageBankConfig 只增不改 | repowiki/ 每仓一份 / capture 显式传参 / 确认闸门对等 | **excluded**：全部等价或前提不成立（无云端、无多用户） |

## 4. 结论

hindsight 与本仓架构前提几乎完全相反：它是**重基建、全自动、每次摄入都烧 LLM** 的云端记忆服务（Postgres + embedding + cross-encoder + 三段 LLM 管线），本仓是**文件即存储、显式确认闸门、LLM 外置**。按「竞品机制价值取决于自身架构前提」的既定判断，引擎层（consolidation、4 臂检索、mental model）大多落 deferred/excluded。

真正值得带走的全在**集成层的认知**里：

- **一条 absorbed 原则（#1）**：索引抑制——注入块列内容清单会让搜索失效，这是 40 轮实测数据背书的设计约束，直接约束本仓未来任何会话注入的形态。
- **一条 absorbed 小改（#3）**：distill/聚合 prompt 补「每条变更带 reason」与「NO COMPUTATION」两条规则，防蒸馏幻觉的低成本护栏。
- **两条 deferred 主线**：delta 刷新（#2，等再生成成本成痛点）、多臂 RRF 检索（#5，等 query_wiki 多路召回需求）。
- 其余 excluded：或本仓已有等价实现（工具指南、引用致谢、降级留痕、mission 外置），或威胁模型/前提不成立（Memory Defense、云端 bank）。

再次验证「借鉴调研先证伪」：4740 文件的记忆系统，真正可搬的只有两条 prompt 规则和一条注入设计约束。

## 附：基线

- 仓库：https://github.com/vectorize-io/hindsight
- 克隆位置：D:\repos\hindsight（HEAD 0a58d69，2026-09-19）
- 主要阅读面：hindsight-api-slim/hindsight_api/engine/（consolidation、reflect、retain、search）、hindsight-integrations/coding-agents/（README + src/core）、skills/hindsight-docs/
