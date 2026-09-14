### 2026-09-14 15:17

### 2026-09-14 实施完成（提前于发版本，用户指令「按设计文档开发」）

三批次全部落地，`tests/test_outcome_telemetry.py` 20 例全绿：

- **批次① 采集**：`telemetry.py` 新增 `record_outcome`（plain append，可选 task_id/note/adopted_key 字段缺省省略）+ `last_adopted_key_for_doc`（adopted 关联抄 key，keys=set() 语义=谱系已知无匹配则不抄，None=doc 级最近采纳）；新工具 `report_outcome`（`outcome_report.py`，registry 双处注册，53 工具）；`store.py` 新增 `KnowledgeStore.session_ids_for_task`（绑定反向查找，live+consumed）。
- **批次② 聚合**：`aggregate_usage` 条目扩展 success/failure 计数（非法 result 跳过）；`wiki_stats` 露出 outcome 段（success/failure/outcome_ratio，与 confidence 并排，零事件不带段）。
- **批次③ 反哺**：distill/consolidate prepare 携带 `negative_examples`（近 30 天 failure、上限 5、newest-first）+ 规避提示语，纯 observe。

实施中发现并修复：任务谱系已知但无匹配采纳时，空 keys 集误回退 doc 级匹配会跨任务错挂采纳 key（`keys or None` 的坑）——改为 keys=None 才表示无谱系线索。

E2E 在本仓真实语料验证过（写路径事件落盘→聚合→wiki_stats→consolidate prepare 反哺全链路），遥测噪音已还原。ruff 存量 F401（distill_conversation.py:544 parse_frontmatter）与本次无关未动。
