### 2026-09-12 13:48

### 2026-09-12（任务记忆检索与自动压缩设计定稿）

Wayfinding + grilling 两轮定稿设计文档 docs/任务记忆检索与自动压缩设计.md（本任务新增设计输入），排期 Phase5 批次二之后。核心决策（Q1-Q10 全按推荐）：

1. **瓶颈定位**：检索缺失而非上下文预算（13 任务/最大 17KB 未失控；单任务读取已有三层防护）。缺口：①任务内旧条目（截断/已压缩）关键词找不回；②跨任务只能靠标题；③压缩需显式触发可能被忽略；④tasks/ 完全不在 BM25 语料。
2. **新动词 search_task_memories**（正是 KnowledgeStore 动词式门面缺的）：单任务条目级检索（### 日期 头一条一索引记录），include_archive=true 默认、include_others=false 默认（搜索侧隐私不宽于读取侧）。
3. **索引复用 AnalysisCache** SQLite upsert 通道（wiki_search.py:356-358），key=tasks/<id>/memories/<user>.md::<n>，索引 gitignore 可重建；**惰性新鲜度**：search 时 mtime/条目数校验重建脏任务（否决写路径同步更新——三个写路径挂钩子漏一处即静默漂移；否决全量重建）。
4. **压缩与检索正交**：压缩省注入成本，archive 条目照常可搜（archived 标注 + 原文可取回），不白压。
5. **自动压缩**（用户定案：无需确认）：get_task_context 在 compaction_due 时返回值携带 compaction_work（prepare 好的待压缩条目+摘要指令），Agent 顺手 submit；否决 Mode B 后台压缩（成本不可见）与机械压缩（丢结论）。
6. **不并 query_wiki 语料**：任务记忆与 Wiki 分轨，活性数据不污染 usage heat；跨任务发现走 list_tasks 标题轻路径。

CONTEXT.md 已加 memory recall 术语。实施切分三批次：①检索动词+索引（不动 get_task_context 主路径）→②自动压缩 compaction_work→③测试+E2E（他山之石 44 条压缩史是最佳回归样本）。handler+registry 两处同步、显式传 repo_path。

### 2026-09-12 22:17

### 2026-09-12（memory recall 与自动压缩驱动实施完成）

任务记忆检索与自动压缩设计（docs/任务记忆检索与自动压缩设计.md）已实施完毕，经独立两轴评审（Standards/Spec）+ 修复。变更：

1. **KnowledgeStore.search_memories**（store.py）：条目级 BM25，**检索时内存直算**（实施时发现设计 D3 缺陷：AnalysisCache 的 search_index 是全量 DELETE+INSERT 重建且 BM25 语料统计全表共享——持久化条目会被 wiki 重建静默清掉且污染 query_wiki 排序统计，故改内存方案，偏离已记入设计文档 §五）；复用 kernel 新单点 **bm25_score()**（retrieval.py 导出，消除第三份公式拷贝）。
2. **search_task_memories MCP 工具**（task_manager.py + registry 注册）：include_archive 默认 true、include_others 默认 false（搜索侧隐私不宽于读取侧）；只读不进 _PUSH_ON_WRITE。
3. **自动压缩驱动**：get_task_context 在 compaction_due 时返回 compaction_work，与 compact 的 prepare 走同一构造点 _prepare_compaction_payload()（单点收敛，消除手工复刻）；Agent 顺手 submit，无需用户确认。
4. 测试 tests/test_task_memory_search.py 11 用例（含 legacy-only 任务、他人 archive 双开关、max_results 边界）。

测试：相关 56 绿 + 全量 954 passed/2 skipped（修复前基线，修复后复跑中）。本仓真实数据 E2E：他山之石 49 条语料（26 archived）召回 teamai-cli/claude-mem 旧条目均命中，产品维护（legacy-only）正常，只读无现场污染。

评审修复项：CONTEXT.md memory recall 词条改「内存直算」、capability-matrix 登记两行、bm25_score 上提 kernel、prepare/compaction_work 共享构造、三个缺口测试。评审误报不改：空 compaction_work 循环（_compaction_needed 合取条件蕴含 entries>keep，切片非空）；est_tokens /4 中文低估（全仓统一口径，留统一调优）。遗留：cache.py/wiki_search.py 的旧内联 BM25 公式迁移到 bm25_score 留待下次重构（已在新 helper docstring 标注）。提交待用户指示。

### 2026-09-14 11:38

### 2026-09-14（BM25 内联迁移完成）

retrieval kernel 三份公式拷贝收敛为单点：cache.py（SQLite 路径）与 wiki_search.py（JSON 路径）的旧内联 BM25 公式改调 bm25_score()；helper 补 max(0.0) idf 钳制保真旧语义（Okapi 变体数学上恒非负，钳制为行为对等保留）。验证：新旧公式 4 组构造用例数值恒等（< 1e-12）+ 本仓 285 条语料三条查询冒烟正常 + 全量复跑中。

踩坑（第二次同类）：ruff --fix 又清掉了 cache.py 的 re-export（USAGE_RANKING_DEFAULTS/load_usage_ranking_config/STOPWORDS 供 tests/test_usage_ranking import），致全量收集失败——已恢复并加 noqa 注释。铁律确认：**再导出必须逐个加 noqa + 注释声明消费者**，否则 ruff --fix 必清。数值等价验证法（构造用例对照旧公式）适用于所有纯收敛重构。
