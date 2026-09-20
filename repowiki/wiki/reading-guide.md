---
type: Concept
title: 阅读指南
generated:
  by: codewiki/reading_guide.py
  at: 2026-09-20 05:06:43+00:00
stale_after: '2027-03-19'
description: '> 基于 PageRank 依赖分析自动生成。排名越靠前的组件被越多模块依赖，建议优先阅读。'
status: stable
verified:
- by: codewiki/5.10.1
  at: '2026-09-20T05:54:18Z'
---
# 阅读指南

> 基于 PageRank 依赖分析自动生成。排名越靠前的组件被越多模块依赖，建议优先阅读。
> 排序依据为 PageRank 得分（综合考虑被依赖数量及依赖方自身的重要性），
> 表中「直接被依赖数」列为原始入度，仅供参考。

## 推荐阅读顺序

| # | 组件 | 类型 | 所属模块 | 直接被依赖数 | PageRank | 文件 |
|---|------|------|----------|--------------|----------|------|
| 1 | `CLILogger.debug` | method | - | 114 | 0.0161 | codewiki\cli\utils\logging.py |
| 2 | `LazyComponentStore.items` | method | - | 130 | 0.0116 | codewiki\mcp\cache.py |
| 3 | `TreeSitterTSAnalyzer._get_node_text` | method | - | 26 | 0.0074 | ...\be\dependency_analyzer\analyzers\typescript.py |
| 4 | `NamespaceResolver.resolve` | method | - | 123 | 0.0069 | ...iki\src\be\dependency_analyzer\analyzers\php.py |
| 5 | `TreeSitterTSAnalyzer._find_child_by_type` | method | - | 19 | 0.0054 | ...\be\dependency_analyzer\analyzers\typescript.py |
| 6 | `TreeSitterJSAnalyzer._get_node_text` | method | - | 19 | 0.0046 | ...\be\dependency_analyzer\analyzers\javascript.py |
| 7 | `CLILogger.error` | method | - | 33 | 0.0041 | codewiki\cli\utils\logging.py |
| 8 | `CrossServiceMatcher.match` | method | - | 38 | 0.0034 | ...ency_analyzer\analysis\cross_service_matcher.py |
| 9 | `LazyComponentStore.values` | method | - | 42 | 0.0034 | codewiki\mcp\cache.py |
| 10 | `TreeSitterJSAnalyzer._find_child_by_type` | method | - | 14 | 0.0032 | ...\be\dependency_analyzer\analyzers\javascript.py |
| 11 | `CallRelationship` | class | - | 19 | 0.0029 | codewiki\src\be\dependency_analyzer\models\core.py |
| 12 | `Node` | class | - | 19 | 0.0029 | codewiki\src\be\dependency_analyzer\models\core.py |
| 13 | `KnowledgeStore.relpath` | method | - | 29 | 0.0028 | codewiki\src\store.py |
| 14 | `TreeSitterJSAnalyzer._get_relative_path` | method | - | 9 | 0.0026 | ...\be\dependency_analyzer\analyzers\javascript.py |
| 15 | `LazyComponentStore.keys` | method | - | 30 | 0.0025 | codewiki\mcp\cache.py |
| 16 | `TreeSitterTSAnalyzer._add_relationship` | method | - | 8 | 0.0024 | ...\be\dependency_analyzer\analyzers\typescript.py |
| 17 | `load_schema` | function | - | 30 | 0.0024 | codewiki\mcp\tools\page_router.py |
| 18 | `atomic_write` | function | - | 33 | 0.0024 | codewiki\src\store.py |
| 19 | `TreeSitterJSAnalyzer._get_component_id` | method | - | 8 | 0.0024 | ...\be\dependency_analyzer\analyzers\javascript.py |
| 20 | `ModuleProgressBar.update` | method | - | 25 | 0.0022 | codewiki\cli\utils\progress.py |

---
*基于 1973 个组件、3891 条依赖边计算。*