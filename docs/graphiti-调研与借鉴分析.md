# graphiti 调研与借鉴分析

> 调研对象：[getzep/graphiti](https://github.com/getzep/graphiti)（本地克隆 `D:\repos\graphiti`，HEAD `de8eb5b`，2026-09-17）
> 调研日期：2026-09-18 · 关联任务：他山之石

## 一、项目定位

graphiti 是 Zep 出品的「时间感知知识图谱」（temporal knowledge graph）记忆框架，为实时 Agent 记忆设计。核心代码在 `graphiti_core/`，支持 Neo4j / FalkorDB / Kuzu / Neptune 等图数据库后端，摄取-检索全链路 LLM 驱动。

## 二、工作机制

### 1. 摄取流水线（`add_episode`，graphiti.py:1043）

```
episode（消息/文本/JSON）
  → 取最近 N 条 episode 作上下文（RELEVANT_SCHEMA_LIMIT）
  → LLM 抽取实体节点 + 关系边（Pydantic schema 约束输出）
  → 节点三级去重（见下）
  → 边去重 + 矛盾检测（见下）
  → 节点属性抽取 + 摘要生成（批量 flight 并行）
  → 嵌入生成 → 落图数据库
```

官方明确建议**异步队列执行、episode 串行 await**（graphiti.py:1119-1122）——摄取是重活，不阻塞主流程。

### 2. 三级实体去重（node_operations.py:627 `resolve_extracted_nodes`）

这是最精华的部分——**确定性快路径优先，LLM 只做兜底**：

| 层级 | 机制 | 代码位置 |
|---|---|---|
| ① 语义召回 | 每个新实体名做余弦相似搜索，取候选 | `_semantic_candidate_search` |
| ② 精确匹配 | 归一化名（小写+空白折叠）完全相等 → 直接合并 | dedup_helpers.py:236 |
| ③ 模糊匹配 | MinHash/LSH（3-gram shingle，32 排列，Jaccard ≥ 0.9） | dedup_helpers.py:255-277 |
| ④ LLM 兜底 | 前三层未决的批量送 LLM 裁决（`duplicate_candidate_id=-1` 表示无重复） | `_resolve_with_llm` |

两个防御细节：

- **熵门控**（dedup_helpers.py:52-85）：短名/低熵名（如 "Sam"）跳过模糊匹配直接升级 LLM——shingle 集对短名不可靠；
- **类型提升**（`_promote_resolved_node`）：泛型 `Entity` 节点被具体类型重复命中时，把具体类型标签合并回去，不丢信息。

### 3. 边级矛盾检测与时间感知失效（edge_operations.py:623）

新边抽取后，与图中**同端点的既有边**对比：

- **fact 逐字相同** → 快路径直接复用，只追加 episode 引用（edge_operations.py:684-695）；
- 否则 LLM 一次调用同时判两件事：`duplicate_facts`（重复）+ `contradicted_facts`（矛盾）；
- 被判矛盾的旧边**不删除**，设 `invalid_at`（事实失效时间）+ `expired_at`（记录失效时间），新边带 `valid_at`（事实生效时间）——历史完整可查（edges.py:271-282）。

### 4. 属性 overlay 合并（node_operations.py:816-833）

LLM 抽取属性时**漏抽/超限丢弃的字段保留旧值**（`merge_mode='overlay'`），只有显式返回的字段才覆盖。注释明确说明：返回 `{}` 会清掉上一次 typed pass 存的属性，是 bug 源。边路径用 `'replace'`（schema 变更时旧属性整体作废）。

### 5. 检索：多路召回 + 可插拔 reranker（search/）

- 召回：BM25、余弦相似、BFS 图遍历；
- Reranker：**RRF**（倒数排名融合，search_utils.py:1775）、MMR、cross-encoder、node-distance（到中心节点的图距离）、episode-mentions（被提及次数）；
- 16 个预置 recipe（`search_config_recipes.py`），按 edge/node/community/episode 四类对象分别配置，组合成 `COMBINED_HYBRID_SEARCH_RRF` 等。

### 6. 社区检测（community_operations.py）

label propagation 聚类（纯 Python 实现，不依赖图库）+ 两两摘要归并（`build_community`，奇数个摘要时 odd-one-out 下一轮再并）生成社区节点，供高层检索。

### 7. LLM 输出防御性校验

所有 LLM 返回的索引 ID 都做范围校验：越界剔除 + warning、缺失 ID 告警、重复 ID 忽略（node_operations.py:560-601）——**模型输出错乱时流程确定性不崩**。

## 三、值得 CodeWiki 借鉴的

| # | 借鉴点 | graphiti 依据 | CodeWiki 现状与落点 |
|---|---|---|---|
| 1 | **确定性快路径 + LLM 兜底的分层去重** | 精确匹配/MinHash 先行，LLM 只裁未决 | CodeWiki 冲突检测（conflict_case.py）目前纯 LLM 判断。笔记标题/别名精确归一化匹配可先做零成本快路径，语义相近的才升级 LLM——省 token 且结果更稳定 |
| 2 | **事实级时间戳软失效** | `valid_at`/`invalid_at`/`expired_at` 三时间戳，旧事实不删只降状态 | ADR-0009 的 supersede 是单行标记 + 单 ref；可借鉴给笔记/任务记忆加「失效时间」维度，`lint_wiki`/`query_wiki` 能按时间过滤过期知识 |
| 3 | **属性 overlay 合并** | LLM 漏抽字段保留旧值，防清空 | `note_merge`/`consolidate_notes` 场景直接适用：合并笔记时 LLM 输出缺的 frontmatter 字段应保留原值而非置空 |
| 4 | **检索 recipe 预设化** | 16 个命名 SearchConfig 组合 | CodeWiki 已有 mode（check/full/by_file），可再进一步：把「BM25×authority×heat + 图扩展 + top-k」打包成命名预设（如 `hybrid_default`、`cheap_check`），调用方一行选定，减少参数面 |
| 5 | **LLM 输出防御性校验** | 越界 ID 剔除、缺 ID 告警、流程不崩 | 蒸馏 submit / 冲突裁决等 LLM JSON 入口都应有同款校验：坏字段剔除+日志，而非整体失败 |
| 6 | **摄取异步化 + 串行保证** | 官方文档明确要求队列化、episode 串行 | CodeWiki 的蒸馏已是后台 subagent，方向一致；可借鉴「同任务 raw 按时间串行蒸馏」的显式约束 |

## 四、不建议借鉴的

- **图数据库 + embedding 全家桶**：graphiti 的价值建立在 Neo4j/FalkorDB + 向量索引上；CodeWiki 的定位是零依赖单机 Markdown + BM25（ADR-0001 已论证自洽），引入图库违背「工具做确定性簿记」的轻量哲学。
- **自动社区摘要**：每次 `add_episode` 可选触发社区重算，LLM 成本高，且自动改写聚合内容与 CodeWiki「入库必经显式确认闸门」的核心原则冲突。
- **边级 LLM 矛盾检测的调用密度**：graphiti 每条新边一次 LLM 调用判重+判矛盾；CodeWiki 笔记粒度大、数量少，照搬会过度调用。取其「软失效」语义即可，检测时机仍应留在显式 lint/consolidate。

## 五、一句话总结

graphiti 最值得带走的不是它的图架构，而是三个工程习惯：**能用确定性算法解决的不惊动 LLM**（分层去重）、**旧知识失效而非删除**（时间戳软失效）、**永远不信任 LLM 输出的形状**（防御性校验 + overlay 合并）。这三条与 CodeWiki 的 Team Doctrine 高度同构，属于低成本高回报的补强。
