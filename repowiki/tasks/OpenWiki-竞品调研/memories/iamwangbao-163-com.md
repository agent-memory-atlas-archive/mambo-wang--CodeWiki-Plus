### 2026-09-17 19:23

mem0（mem0ai/mem0）竞品调研完成：报告落盘 `docs/compare/mem0-notes.md`（含第 7 节「Agent 宿主 Hook 插件体系」及借鉴评估），遵循 openwiki-notes.md 格式惯例，全部论断标注源码行号；源码克隆在 `%TEMP%\mem0-research`。

### 2026-09-17 19:23

核心借鉴点按性价比排序：整数 ID 反幻觉映射（distill/consolidate 的 UPDATE/MERGE 路径）、单次 LLM 调用输出事件流（submit 协议加 event 字段）、MD5 哈希前置去重（ingest_note）、混合打分+语义门槛门控（query_wiki）、SQLite history 账本、SKILL.md 分发渠道；明确不借鉴自动 UPDATE/DELETE 无确认闸门。

### 2026-09-17 19:23

hook 机制评估结论：不做架构改动（核心哲学已同构）；留观察点——若 CodeBuddy 给 Stop/PreCompact 事件补上 transcript 增量，可参考 mem0 的 `checkpoint_due` 阈值模式实现中途 checkpoint。

### 2026-09-17 19:23

mem0 2025 年删除全部图数据库驱动（PR #4805，约 4000 行）改轻量实体链接，验证了 CodeWiki ontology.yaml 不引入图库的路线。
