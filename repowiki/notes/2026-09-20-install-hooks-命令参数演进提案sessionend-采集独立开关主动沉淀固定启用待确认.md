---
type: decision
title: "install-hooks 命令参数演进提案：SessionEnd 采集独立开关、主动沉淀固定启用（待确认）"
tags: ["decision", "sessionend"]
metadata:
  date: 2026-09-20
  confidence_level: weak
  task_id: 产品维护
  source_session: "7c6e728aee994ae8ac04574de53d3cfd"
  related_modules: ["cli", "mcp"]
  severity: medium
  source_ref: "conversations/conv-user_command-commands-codewiki-启用-禁用任务管理（跨会话任务记忆）-管理-team-me-37c9c2.md"
  scene: "产品维护/接线档位"
status: draft
author: iamwangbao-163-com
generated: { by: codewiki/5.10.1, at: 2026-09-20T06:59:00Z }
stale_after: 2027-09-20
origin: conversation

---

## Background

2026-09-20 会话中用户对 `codewiki/启用/禁用任务管理（跨会话任务记忆）` 命令提出参数演进需求：当前 `codewiki install-hooks --active-settle on|off` 把主动沉淀叠加与 hook 接线绑在一起，用户希望解耦。

## 提案内容（截至本次采集尚未定论，处于 grilling 讨论中）

1. SessionEnd 采集 hook 单独一个开关，与主动沉淀解耦；
2. 去掉 `--active-settle` 参数，主动沉淀机制改为固定启用；
3. 产品目标：主动沉淀效果好的话，就不用采集对话和补蒸馏（catch-up distillation）了——主动沉淀成为任务记忆的主通道，采集+补蒸馏退为兜底。

## Rationale

该提案决定 install-hooks CLI 参数面与任务记忆双通道（主动沉淀直写 vs 采集+蒸馏）的长期演进方向，后续实现或修改接线逻辑的 Agent 需知此方向正在讨论中。相关现状代码：`codewiki/cli/commands/install_hooks.py`、`codewiki/cli/utils/ide_config.py`、`codewiki/hooks.yaml`；既有设计文档：`docs/接线档位选择设计方案.md`。与既有决策笔记 `notes/2026-09-18-任务记忆通道互斥固定语义补蒸馏task-id-过滤固定不提取记忆无开关记忆归主动沉淀直写.md`（通道互斥语义）与 `notes/2026-09-18-主动沉淀协议三缺口修复判据扩面每轮收尾自查双通道独立声明active-settle-块.md`（协议缺口修复）主题相关但事实不同：那两条是已定论的通道语义与协议实现，本条是尚未收敛的 CLI 参数面演进提案。

## 状态

用户以 /grill-with-docs 发起压力测试，本次采集时点讨论尚未收敛，未形成最终决策；最终结论以后续会话产出的决策笔记为准，确认后可合并/取代本条。
