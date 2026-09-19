---
type: decision
title: "llm-wiki-compiler 调研处置：10 候选 0 采纳 / 3 deferred / 7 excluded"
tags: ["decision", "typescript"]
metadata:
  date: 2026-09-19
  confidence_level: weak
  task_id: 他山之石
  source_session: "c07baaa505eb4d5e8a426636266c63a0"
  related_modules: ["docs"]
  severity: medium
  source_ref: "raw\\conv-working_memory_content-The-following-is-the-existing-working.md"
  scene: "竞品调研（他山之石）"
status: draft
author: iamwangbao-163-com
generated: { by: codewiki/5.10.1, at: 2026-09-19T01:17:41Z }
stale_after: 2027-09-19
---

## Background

2026-09-19 对 atomicstrata/llm-wiki-compiler（llmwiki，Karpathy「LLM Wiki」模式的通用知识编译器，TypeScript/[Node](../../codewiki/src/be/dependency_analyzer/models/core.py)≥24，v1.3.0，单人主导、活跃）做了源码级调研，报告存档于 `docs/llm-wiki-compiler-调研与借鉴分析.md`。

其核心机制（均经代码核对）：CLP 配置化生命周期 profile（`.llmwiki/profile.json` 声明实体/关系/FSM/信任门，引擎无领域分支、fail-closed）；意图日志 + 单一变更执行器（pending 记 pre-state，crash 后 replay 整体回滚，apply 时重新断言底线，见 `src/trust/journal.ts`、`executor.ts`）；计算式 freshness 四态（fresh/stale/orphaned/unverified，按需计算不持久化）；eval 量化 harness（health/引用覆盖率/graph health 评分 + 阈值门禁 + 历史 delta）。

## Decision

10 个借鉴候选处置为 **0 采纳 / 3 deferred / 7 excluded**：

- **deferred**（真差异主线，待真实消费场景再启动）：① lint 升级为量化评分 + 阈值门禁 + 历史 delta；② 多文件批次意图日志（当前 markdown 场景风险低）；③ confirm 前质量预评（①的自然延伸）。
- **excluded**：freshness 四态（本仓 `evidence.py:110` 已有 ok/stale/missing/unresolvable 等价实现）、profile-as-data（schema.yaml 已是）、OKF 交换格式、review 扣留、query 复利、TS 栈/重运行时（主动不同取向）。
- **不立项但值得吸收的工程习惯**：apply 时重断言底线（对应本仓 confirm 时按当前约定重校验）、诚实边界写进代码注释、已知范围限制就地标注。

## Rationale

再次验证「借鉴调研先证伪」：一半以上候选（7/10）本仓早有等价物，若不先在本仓搜等价实现就会重复造轮子。deferred 项的共同前提是「先有真实消费场景」——成本可见性优先于新造能力。

## 适用范围

后续重启 deferred 候选（量化 lint、批次意图日志、confirm 前预评）时，以本决策为基线，先确认消费场景是否出现；对同类知识编译器（OKF 系、profile-as-data 系）做调研时可直接引用本处置表避免重复评估。与既有笔记『借鉴调研的排除判据』（通用判据层）、『他山之石增量调研流程』（流程骨架层）互补：本条是具体项目的处置结论层。
