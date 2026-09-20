---
type: task
task_id: outcome-采集
title: outcome 采集
status: completed
created_at: 2026-09-14T06:38:00.788196+00:00
completed_at: 2026-09-14T07:26:25.127297+00:00
---

落地 docs/负反馈与经验通道设计方案.md：三批次（①report_outcome 采集 ②聚合+wiki_stats ③蒸馏反哺 negative_examples）。

关键约束：
- 遥测事件不是落盘知识，免确认闸门（ADR-0002 同理）；不碰 frontmatter（不新增第 5 个写入路径）
- 事件双挂 doc+task_id，result 二值 success/failure，note 一句话上下文；adopted 关联抄 key
- 消费全 observe：聚合/wiki_stats 展示、prepare 提示；disputed_assets lint check 不实施（登记 off）
- 排期：下一版发布之后（发版本优先）
- 验收链见设计文档 §八
