---
type: Conversation
title: "conversation 20260919T144726Z"
status: distilled
stale_after: 2026-12-18
generated: { by: codewiki/5.10.1, at: 2026-09-19T14:47:26Z }
active_settle: true
captured_at: "2026-09-19T14:47:26Z"
content_hash: "sha256:9564e719ed60dc01529ad104dc771c5f9a6cf862494359922fadacb92c3e3f94"
friction_score: 0
friction_signals: "correction=0,interrupt=0,repeat=0,user_turns=1"
keep_raw: false
link_to: ""
source_session: ""
task_id: "他山之石"
turn_count: 2
---

# Conversation Transcript

user: https://github.com/vectorize-io/hindsight  调研项目
assistant: hindsight 调研完成，报告落盘 docs/hindsight-调研与借鉴分析.md。基线：克隆 D:\repos\hindsight，HEAD 0a58d69（2026-09-19 当日提交，约 4740 文件）。定位：vectorize.io 的生物拟态长期记忆系统（hindsight-api Python 引擎 + coding-agents TS 集成包接 18 个编码 Agent），重基建重 LLM（Postgres+embedding+cross-encoder，每次 retain 都跑 LLM 提取），与本仓「工具无状态、LLM 外置」架构前提相反。核心机制（代码核对）：①consolidation prompt 九条合并规则，每条 op 必带 reason，NO COMPUTATION（不做算术推断只记明说的数字），Mission 优先于处理规则（领域定制放数据不放代码），语言保持规则（observation 用源事实语言，混语合并多数胜出）；②knowledge pages delta 刷新（增量编辑而非重建，trigger 字段级 merge，五页固定分类法每页钉死一个知识层 tag，Jenkins H 语法错峰）；③4 臂检索（semantic/bm25/graph/temporal）+ 每臂截断 + RRF 融合 k=60；④retraction：文档 based_on 失活 fact id 自动撤回依据，纯 dict 变换无 LLM；⑤索引抑制：注入块列知识页清单导致 40 轮实测 0 次搜索（全拿注入 id 直接 read），只说「N 页覆盖本仓库，请调 search」；⑥when-to-call 工具指南每 10 轮重注入。处置：absorbed 2（索引抑制为注入设计约束——本仓现状已部分符合；reason 必带 + NO COMPUTATION 两条 prompt 规则吸收进 distill/聚合 prompt）、deferred 2（page delta 刷新等再生成成本成痛点、4 臂 RRF 等 query_wiki 多路召回需求）、excluded 8（工具指南/引用致谢/降级留痕/mission 外置等本仓已有等价；Memory Defense/云端 bank 前提不成立）。再次验证「借鉴调研先证伪」：4740 文件的记忆系统，真正可搬的只有两条 prompt 规则和一条注入设计约束。
