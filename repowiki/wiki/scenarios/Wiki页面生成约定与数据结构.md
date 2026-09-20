---
type: Scenario
title: Wiki页面生成约定与数据结构
description: OKF status 分层与 actor、module_tree 遍历、模板包内单源收敛、schema.yaml 聚合阈值、聚合候选 disposition
tags:
- CodeWiki-CN
generated:
  by: codewiki/5.8.0
  at: '2026-09-08 05:55:14+00:00'
stale_after: '2026-12-07'
aliases:
- Wiki页面生成约定与数据结构
status: stable
metadata:
  generated_from: f08feab
  resource: repo://CodeWiki-CN
  code_fingerprint: sha256:829467a7f49459ddf16d1711753a335b7338eb7409360e8d30565d9f78d11621
  source_notes:
  - notes/2026-09-05-schemayaml-模板双源收敛为包内单源删根副本守卫测试只验包内模板清理-init-wikischema-gener.md
  - notes/2026-09-07-consolidate-notes-候选-disposition-三值机制未入选笔记不再无声滞留excluded-必填.md
  - notes/2026-09-05-doc-similaritypy同源判定用正文-shingle-的-minhash-bottom-k-sketch-ja.md
  - notes/2026-09-05-frontmatter-sources-有三个生产者字段形态各不相同.md
  - notes/2026-09-05-frontmatter-的-sources-是采样锚点不能当作文档覆盖率声明.md
  - notes/2026-09-05-ingest-source-冲突同源确认闸门四层l0-sha-256-l1-version-sibling-语义指纹-l.md
  - notes/2026-09-05-registry-backfill-在提前-return-分支会丢失version-sibling-拦截时须-save.md
  - notes/2026-09-05-sources-wiki-sources-raw-sources-source-refs-四处同名语义完全不同.md
  - notes/2026-09-05-stale-evidence-只驱动复核提醒仅处理带-content-hash-的条目报-warning-且不自动改写.md
  - notes/2026-09-05-unsupported-claims-只扫带-confidence-xxx-的规则行且只做格式邻近性检查不校验语义支撑.md
  - notes/2026-09-05-wikiindexmd-条目-summary-复用页面-description-时相对链接失效-render-index.md
  - notes/2026-09-05-删除-rawsources-下某-source-前先盘点引用与-source-id-所有权删后-10-页断链-readm.md
  - notes/2026-09-10-已落库结论变更的更新流程wiki-页-edit-doc-file-原地改笔记新写reject-note-旧的confir.md
  - notes/2026-09-10-删除导入文档的三种路径源文档-retract-source先-dry-run笔记-reject-notewiki-页面无.md
  - notes/2026-09-10-retract-sourceremove-refs-不清理-metadata-嵌套的-source-refslint-s.md
  - notes/2026-09-07-旧生成器-frontmatter-metadata-listmapping-混合坏结构会静默崩溃全库索引重建异常被吞.md
  summary: 补入结论变更更新流程、删除资产三路径、retract_source 嵌套 source_refs 漏清、frontmatter 坏结构静默崩溃索引
  heat: 6
  confidence_level: weak
---
## 工作场景
wiki 页面生成的 OKF/frontmatter 约定、数据结构消费与知识资产治理（模板分发、聚合可审计性）。适用于撰写/修补 wiki 页面、开发实体概念提取、排查 frontmatter 与模块树、配置聚合与模板分发、执行 consolidate_notes。

## 适用条件
开发 write_doc_file / extract-knowledge、写 OKF 测试、遍历 module_tree.json、调整聚合阈值/模板分发、判定聚合候选去向。

## 核心 SOP
1. status 语义分层：`write_doc_file` 代码生成页默认 stable；ingest_note/distill 经验笔记保持 draft（confirm 闸门）。
2. OKF actor 写 `codewiki/<version>`（`config.py actor_id()`），排查先看实际返回值。
3. 遍历 module_tree.json 先判断 children 元素类型：字符串引用需二次查顶层定义节点。
4. 实体/概念提取「识别与举证分离」四步：骨架提取 → query_wiki 语义去重 → 证据校验 → 编译式撰写。
5. 生成路径与修补路径都要写 aliases，两套路径默认键集合保持一致。
6. `lint --fix=true` 自愈顺序：预扫 stale_refs → rebuild_index → 再跑全部检查。
7. doctrine 备份机制已移除（.backup 冗余且污染检索索引）。
8. 聚合/doctrine 阈值等运行参数通过 `repowiki/schema.yaml conventions.aggregation` 覆盖，不改 py 源码默认值。
9. ingest_note 自动写索引；close_session 兜底终态确保索引一致。
10. **配置/脚手架模板收敛为包内单源**：删根副本与 fallback（`init_wiki._SCHEMA_TEMPLATE_ROOT`、`schema_generator._CONFIG_PATH_ROOT`，包内模板存在时永不生效），守卫测试只验包内权威副本。典型事故：开关只加进根 `schema.yaml`，而实际分发的是包内模板 → 新工作区静默拿不到开关。
11. **聚合候选必须有去向**：每条 pending 记 `metadata.disposition{verdict, reason?, at}`——absorbed 走 source_notes ⇄ consolidated_into，deferred 保留在 pending 并回带 disposition，excluded 必填 reason 并永久退出 pending；写回复用既有 `_update_frontmatter_meta`（locked RMW），不新建写回路径。
12. **frontmatter sources 是采样锚点，不是覆盖率声明**：判断文档是否覆盖某文件看 module_tree / component_count，不是数 sources 条数；生成链路有两道截断。
13. **sources / wiki-sources / raw-sources / source_refs 四处同名语义完全不同**：frontmatter sources 是 OKF 代码证据（唯一消费者 lint 的 stale_evidence）；wiki/sources/ 是三方文档页目录；raw/sources/ 是导入源文件；source_refs 是笔记溯源引用。改代码前先分清对象。
14. **frontmatter sources 有三个生产者，字段形态各不相同**：_inject_evidence（id/resource/content_hash）、_okf_sources_block（额外带 provenance）、ingest_source——可据字段形态反推来源。
15. **stale_evidence 只驱动复核提醒**：仅处理带 content_hash 的条目，报 warning 且不自动改写；纯外部源条目不受约束。
16. **unsupported_claims 能力边界窄**：只扫带 `(confidence: x.xx)` 的规则行，只做格式邻近性检查（后续 2 行内有 `> Evidence:`），不校验语义支撑——没标置信度的断言完全绕过。
17. **doc_similarity 同源判定**：正文 shingle（中文按字 3-gram / 英文按词）MinHash bottom-k sketch（k=128），标题从 shingle 中剔除；阈值只决定告警强度（HIGH 0.50 / LOW 0.25）。
18. **ingest_source 四层确认闸门**（只警告不落盘）：L0 SHA-256 字节去重 → L1 version_sibling 语义指纹 → L2 同名不同内容 conflict → L3 frontmatter supersedes。任何被算过的条目都要标记并落盘（提前 return 分支也须 _save_registry）。
19. **删除 raw/sources 前先盘点引用与 source id 所有权**：source id 可能被多个页面 frontmatter/正文引用，删后断链不可逆；先查引用面再删。
20. **wiki/index.md 条目 summary 复用页面 description 时相对链接失效**：_render_index 须按 relpath 重写链接，否则模块页 description 里的相对链接在 index 上下文断链。
21. **已落库结论变更的更新流程**：wiki 页（queries/comparisons）用 edit_doc_file 原地改；笔记新写 + reject_note 旧的 + confirm 新的；ADR 须回源同步。方向变则新写 decision 笔记，仅表述/证据变则原地改。
22. **删除导入文档的三种路径**：源文档 retract_source（先 dry_run，remove_refs 模式不清理 metadata 嵌套的 source_refs，lint stale_refs 也漏）；笔记 reject_note；wiki 页面无工具级删除。
23. **旧生成器 frontmatter 坏结构会静默崩溃全库索引**：孤儿 list 项 + mapping 键混合结构 → YAML 解析为 list → retrieval.py 的 _meta.get() AttributeError → build_full_index 崩溃且异常被吞。修复后全库索引恢复。

## 判断逻辑
- 去重三条件：同一真实事物 / 名称变体 / 类型兼容；核心原则 related ≠ same。
- health_score 是扣分制（error -10 / warning -3 / info -1）。
- 双份分发本身就是 bug 源：功能加了但分发模板没跟上 = 静默降级。
- 借鉴外部建议先过代码核对，并纠正方向映射（生成侧「候选无声消失」 vs 聚合侧「候选无声滞留」，是同一可审计性缺口的相反方向）。

## 禁忌与反模式
- 不全局改 `inject_okf_frontmatter` 的 status 默认值；不用 `agent:codewiki/` 旧格式 actor。
- 不用嵌套 dict 假设遍历 module_tree。
- 不给 doctrine 做文件级 .backup；不在 py 源码硬编码聚合阈值。
- 不让未入选的候选无声滞留（无 disposition 会让计数器长期告警、每轮重复权衡）。

## 关键事实依据
- prompt 模板示例曾写 `status: draft` 误导 LLM 照抄产生 draft 页面，模板已同步改 stable。
- disposition 三值机制：4 处约 40 行，excluded 无 reason 直接进 errors。
- 长期 deferred 告警阈值暂不设定（等 disposition 积累几轮再定）。