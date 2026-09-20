# llm-wiki-compiler（llmwiki）调研与借鉴分析

> 调研日期：2026-09-18 · 任务：他山之石 · 方法：克隆源码读代码（D:\repos\llm-wiki-compiler，HEAD c2c85bb，2026-09-17），结论均经代码核对，非文档站口径。

## 1. 项目概况

| 维度 | 事实 |
|------|------|
| 定位 | Karpathy「LLM Wiki」模式（gist 442a6bf5）的通用知识编译器：原始素材 → 带引用的可互链 Markdown wiki |
| 技术栈 | TypeScript / Node ≥ 24，MIT，npm 包 `llm-wiki-compiler` v1.3.0 |
| 作者/活跃度 | Ethan Joffe（atomicstrata），单人主导，最后提交 2026-09-17，高度活跃 |
| 输入 | md/txt、PDF（pdf-parse）、URL（readability+turndown）、YouTube 字幕 |
| 输出 | `wiki/concepts|queries|<typed>/` + `.llmwiki/`（state.json、embeddings、candidates、eval） |
| 消费面 | CLI、本地只读 viewer（4 主题）、MCP server、TypeScript SDK、OKF/JSON/JSON-LD/GraphML/Marp/llms.txt 导出 |
| LLM 提供方 | Anthropic / Claude Agent SDK / OpenAI / Ollama / Copilot / OpenAI 兼容网关等，可移植 |

核心叙事：把工作从 query time 移到 compile time——先编译成带引用、元数据、评审状态的类型化页面，查询/上下文包/导出都消费这个编译产物，而非每次重读原始文件（README.md:107-115）。

## 2. 核心机制（代码核对）

### 2.1 CLP：Configurable Lifecycle Profiles（profile-as-data）
- `.llmwiki/profile.json` 声明实体类型/字段契约/有向关系/生命周期 FSM/门控前置条件/工作流/哈希钉住的 artifact/连接器/检索分层（docs/concepts/configurable-lifecycle-profiles.mdx:36-64）。
- 核心不变量：领域行为来自 profile 数据而非硬编码分支，引擎无 `if AutoSci then ...`（同文件 :66-72）。
- 写面强制：页面写入、生命周期迁移、关系写入、artifact 写入、评审批准五个面全部走同一校验，评审批准时还会按当前 profile 重新规划写入（:85-116）——防止 OKF 导入/连接器/工作流等兄弟面绕过门。
- 信任分层：`LLMWIKI_TRUSTED_WRITE` / `LLMWIKI_CONNECTORS` 环境变量控制 live 写权限；连接器只能 stage 评审候选，不能直接落盘；连接器候选批准需 `--draft-content-hash` 钉住批准的就是评审过的正文（:119-130）。
- 模板分发：Ed25519 签名 + 密钥轮换 + 吊销 + 兼容性检查（README.md:103）。

### 2.2 意图日志 + 单一变更执行器（批次原子性）
- `src/trust/journal.ts:1-29`：单存储意图日志，两阶段（pending 记录每个目标的 pre-state → committed），crash 后 `replayJournal` 把未提交批次整体回滚到 pre-state。日志只记 pre-state 不记 post-state，半应用批次只能回滚到完整前态。
- `src/trust/executor.ts:1-59`：所有公开变更面（compile/import/refresh/review-approve/createRelation/transitionLifecycle）收敛到一个加锁执行器 seam；apply 时**重新断言强制底线**（S5），不信任 plan 时的检查仍然成立——手工构造的 mutation 无法走私超限正文。
- 诚实边界写得很清楚：journal 只覆盖页面字节写，approve 的后续尾巴（索引刷新、候选删除）在批外 best-effort；跨存储 co-commit 是 Phase-5 待办（executor.ts:14-26）。无 fsync，掉电不保证（journal.ts:5-9）。

### 2.3 计算式 freshness 层
- `src/freshness/index.ts:19-58`：纯函数、按需计算、从不持久化。四态分类：`fresh`（所有 owner 存在且哈希一致）/ `stale`（部分 owner 失效或哈希漂移）/ `orphaned`（owner 全没了）/ `unverified`（无 ownership 记录或 state 损坏）。有序判定：state 坏 → unverified；orphaned frontmatter 优先；无 owner → unverified。
- `llmwiki refresh --stale` 只修复过期页面，不重编译无关新源（README.md:66）。
- 已知范围限制也写在代码里：typed entity 页面无 ownership 记录，故意归 unverified、排除在 orphan 清理外（index.ts:29-37）。

### 2.4 eval 量化评估 harness
- `src/eval/index.ts:56-75`：`runEval` 并行跑 health、citation coverage、source utilization、citation depth、page health distribution、graph health、stats，full 套件加 judge-model citation support 抽样；产出带 delta（与上次报告对比）和 thresholdViolations（CI 门禁），历史落 `eval/history.jsonl`。
- 语义：不是「有没有问题」的规则检查，而是「质量分数多少、比上次退步没有、是否跌破阈值」的量化门禁。

### 2.5 其他
- Review policy：低置信/矛盾/违规 schema/违规出处四类 hold 模式，候选记录精确扣留原因，拒绝进 `candidates/archive/` 留审计（docs/concepts/wiki-model.mdx:54-61）。
- MCP server：ingest/compile/query/search/read/lint/status/context-pack/eval/verify_artifact + OKF 导入导出 + workflow 四工具（src/mcp/tools.ts:34-43 等）。
- 混合检索：语义 chunk + BM25 重排 + wikilink 图扩展。
- query --save 把答案存成 queries/ 页面参与后续检索——知识复利。

## 3. 与本仓对照处置表

| # | llmwiki 机制 | 本仓现状（代码核对） | 处置 |
|---|--------------|---------------------|------|
| 1 | eval 量化评分 + 阈值门禁 + 历史 delta | `wiki_lint.py` 有 24 项规则检查（_ALL_CHECKS，wiki_lint.py:25），但是布尔式「有无违规」，无综合评分、无阈值配置、无跨次 delta | **deferred**：真差异。lint 报告可加一层聚合评分（如引用覆盖率、断链率、stale 占比的加权分）+ `thresholds.yaml` 门禁 + history.jsonl delta。承接整体报告「成本/预算硬约束」主线之外的质量主线。落地前先确认是否有真实消费场景（CI 门禁 or 手动体检） |
| 2 | freshness 四态（fresh/stale/orphaned/unverified） | `evidence.py:110-119` 已有 ok/stale/missing/unresolvable 四态（content_hash 对比）；lint 有 stale_evidence/stale_sources/stale_notes/orphan_pages 多项检查 | **excluded**：本仓已有等价实现，且 evidence 四态语义更贴代码溯源场景。llmwiki 的「按需计算不持久化」原则本仓已遵守 |
| 3 | 意图日志批次原子性（多文件 mutation 回滚） | `store.py:99-107` atomic_write（temp+rename）+ sidecar lock，单文件原子；无跨文件批次 journal | **deferred**：本仓多文件写场景（consolidate_notes、workspace_bootstrap）目前靠「逐文件落盘+失败继续」的 SOP 兜底。若未来出现「一批笔记必须全成或全不成」的用例（如冲突裁决批量改写），再引入 pre-state journal。当前 markdown 笔记场景风险低，不立项 |
| 4 | CLP profile-as-data（FSM/工作流/信任门） | `schema.yaml` 已是声明式约定（命名/必填章节/freshness 窗口），lint 按其执行 | **excluded**：原则一致（约定即数据、引擎无领域分支），本仓已按此运作。CLP 的实体 FSM/工作流/artifact 哈希钉住对「代码 wiki」场景过重，且依赖 TS 运行时 |
| 5 | 评审批准时按当前 profile 重新规划（防兄弟面绕过） | 本仓确认闸门在 confirm_note 单点，所有落盘必经 draft→confirm；无「批准时重新校验」环节 | **absorbed（习惯）**：confirm_note 时若 schema/约定已变，应按当前约定重校验而非信任 draft 时点。属实现细节自查项，不立项 |
| 6 | OKF 开放知识格式交换 + 签名模板分发 | 本仓已有 okf_conformance 检查（wiki_lint.py:1882）；无签名分发 | **excluded**：交换格式已有；签名模板分发依赖「模板市场」前提，本仓无分发形态 |
| 7 | review policy 四类自动扣留 | 本仓 draft/confirm 闸门 + 冲突检测（ADR-0007 conflicts/ 一等对象） | **excluded**：等价，且本仓冲突检测更细 |
| 8 | query --save 答案复利（queries/ 页面参与检索） | 本仓有 queries/ 页面类型 | **excluded**：等价 |
| 9 | eval 在批准前评估 pending candidates（#226，2026-09-17 新合入） | 本仓 confirm 前只有冲突检测，无质量预评 | **deferred**：与 #1 同根，若做 #1 则此为自然延伸（confirm_note 前跑轻量质量分） |
| 10 | TS 技术栈、viewer UI、混合检索（BM25+embedding） | 本仓 Python + 本地 markdown + 同步 MCP，检索已有 jieba 分词 + 索引 | **excluded**：主动不同取向（stable 笔记：服务端/重运行时类不是缺口） |

## 4. 结论

llmwiki 是「LLM Wiki 模式」阵营里工程完成度最高的参考实现之一，其价值集中在**信任工程**（意图日志、单一执行器 seam、apply 时重断言、诚实边界文档化）与**质量量化**（eval harness）两条线。与本仓对照后：

- **真差异只有一条主线**：lint 从「规则布尔检查」升级为「量化评分 + 阈值门禁 + 历史 delta」的可选层（#1/#9），deferred 待真实消费场景出现。
- **三条工程习惯值得吸收**（不立项、写进做事方式）：① apply 时重新断言底线，不信任 plan 时点的检查（对应本仓 confirm 时按当前约定重校验）；② 诚实边界写进代码注释（哪些保证没有、什么是 future work）；③ 已知范围限制就地标注（freshness index.ts:29-37 的写法）。
- 其余候选均因本仓已有等价实现或属主动不同取向而排除，再次验证「借鉴调研先证伪」stable 笔记。

## 附：基线

- 仓库：https://github.com/atomicstrata/llm-wiki-compiler
- 基线：v1.3.0，HEAD c2c85bb（2026-09-17），下次增量调研以此为基线。
- 本地克隆：D:\repos\llm-wiki-compiler
