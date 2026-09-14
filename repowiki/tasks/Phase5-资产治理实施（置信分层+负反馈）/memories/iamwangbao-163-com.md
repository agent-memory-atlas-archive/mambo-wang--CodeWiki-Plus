### 2026-09-12 08:26

### 2026-09-12

HL-Mem 调研（docs/HL-Mem-调研与借鉴分析.md）对 Phase5 的三条设计输入（2026-09-12 拷问定稿）：

1. **T7 与 C8 的关系修正**：报告初稿曾把「双时间」整体 excluded，但 T7 本来就计划引入 valid_from/valid_to/last_verified_at——不矛盾，排除的只是完整四字段双时间与 recorded_* 轴；T7 按原计划做。
2. **负反馈延寿公式定稿（T5/T6 落地后的顺手项）**：移植 HL-Mem BayesianUsefulnessPolicy 纯函数（domain/feedback.py:36-37）：bonus = floor(正证据/3) × 14 天，cap 180；延长 stale_after 时被该笔记类型新鲜度上限夹住（对齐 HL-Mem valid_to 夹紧 workers/ttl.py:39-43 + service_health 槽位二次夹紧 :44-46）。默认 observe：先只记录「本应延长多少天」不改实际值。
3. **保留冷启动守卫**：_check_low_adoption 零 adopted 事件静默返回（wiki_lint.py:1271-1277）的纪律不得破坏。

三态词汇统一用 tri-state gate（CONTEXT.md glossary 已落）。排期提醒：「冲突一等对象」任务（ADR-0007）与本任务批次二动同一片 note_lifecycle/note_query 区域，须错开。

### 2026-09-14 09:42

### 2026-09-13（批次一完成）

Phase5 批次一（T1-T4 置信骨架）实施完成，在分支 phase5/confidence-skeleton 上（含 234 个迁移文件），全量 970 passed / 2 skipped，评审修复完毕，待用户确认合入。

实现：T1 confidence_level 流转（confirm weak / evidence{test_ref|commit_ref|reviewed_by}→strong+metadata.verification / reject→shadow / ingest 默认 weak / consolidation weak / doctrine strong）+ scripts/migrate_confidence.py 幂等回填（本仓 234 条已跑）；T2 _CONFIDENCE_AUTHORITY{strong+0.10,weak 0,shadow-0.30} 叠加 _doc_authority（clamp 不变，distill 去重 apply_authority=False 豁免核实保持）；T3 query_wiki confidence 露出 + include_shadow 门控 + task_context 排除 shadow；T4 wiki_stats confidence_distribution + strong_ratio + top_shadow_assets（early-return 也带）。

关键语义修正（评审抓出）：draft 保持 weak 可见（[unconfirmed] 前缀语义不变）——shadow 专用于 rejected/misrecalled，初版 draft→shadow 会让 draft 从检索消失，被既有 e2e 测试拦下。frontmatter._parse_block 修了两个坑：嵌套 dict 解析（verification 需要）+ list_key 重置回归，均已加回归锁。流程教训：ruff --fix 会清掉 re-export 的私有名（_resolve_within 致 14 测试断裂）——再导出必须加 noqa 注释说明。

下一批次：T5 flag_misrecall → T6 自动降权+复核清单（新 lint check 记得同步 registry 枚举）→ T8 负例反哺；T7 已独立为新鲜度专项（F1-F3）。合入后注意：迁移后的索引需 build_full_index 刷新才能体现 T2 权重（authority 缓存在索引行）。
