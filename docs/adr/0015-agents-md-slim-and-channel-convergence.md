# ADR-0015: AGENTS.md 托管块瘦身与注入通道收敛

- 状态：已接受
- 日期：2026-09-20
- 关联：ADR-0002（任务记忆直写）、ADR-0010（通道互斥）、ADR-0014（蒸馏只产经验笔记）；docs/接线档位选择设计方案.md §3.3/§3.8/§3.9
- 背景：2026-09-20 竞品调研（任务「他山之石」）：project-cairn、openwiki、better-harness、caveman、teamai-cli、claude-mem、hindsight、letta-code

## 背景与问题

竞品调研发现三个结构性问题：

1. **AGENTS.md 托管块超重**。CodeWiki 块（`zh.yaml`/`en.yaml` 的 `artifacts.agents_md.main`）约 89 行，含六节全文：入口文件、使用建议、标注依据、采纳声明、纠正识别（含 9 行归档示例 JSON）、主动沉淀（含路由表）、语言闸门。AGENTS.md 是每会话常驻上下文，这些全文在 hook 已硬注入 doctrine/知识库概览的时代大部分冗余。
2. **task-memory 协议双通道重复注入**。`_TASK_MEMORY_AGENTS_SECTION`（AGENTS.md 软通道，~40 行）与 SessionStart hook `task_session_start.py` 注入的 system_reminder（硬通道）内容高度重叠——弹框规则、补蒸馏流程、收尾采集几乎逐句相同。违反「单点收敛」原则。
3. **细节已有收敛点但未用满**。`get_prompt("task-workflow")` 与 `get_prompt("ingest-note")` 已存在，但 AGENTS.md 仍全文内联同样的内容。

竞品对照：project-cairn 把 AGENTS.md 压到 ≤60 行路由层（文档职责表 + 仲裁规则）；openwiki 托管块明确「按需上下文，非启动必读」；teamai-cli 用 golden fixture 钉死 hook 渲染输出。我们与 cairn 的差距最大。

## 决策

### D1. CodeWiki 块瘦身（zh.yaml / en.yaml 同步）

保留（行为闭环关键，不可删）：
- 入口文件三链接
- 使用建议四条（压缩为紧凑列表）
- 采纳声明（采纳计数驱动检索排序，删了 `low_adoption` 检查失效）
- 语言闸门

压缩（规则保留，解释与示例外置）：
- 标注依据：三条规则保留，删解释性尾句
- 纠正识别：三步流程 + 纠正信号保留；归档示例 JSON（9 行）删除，指向 `get_prompt("ingest-note")`
- 主动沉淀：触发信号 + 四问过滤 + 路由表保留；执行流程与「不要记录」清单压缩，细节指向 `get_prompt("ingest-note")`

目标：89 行 → ~45 行。

### D2. task-memory 协议收敛为「指针 + 兜底」

`_TASK_MEMORY_AGENTS_SECTION` 从 ~40 行全文压缩为 ~10 行：
- 保留：任务记忆 vs Wiki 笔记的定位一句话、会话开始任务关联的硬性要求（弹框规则一行）、`get_prompt("task-workflow")` 指针
- 删除：弹框细则、补蒸馏五步流程、传统收尾采集全文——这些已由 SessionStart hook 硬通道注入（hook 宿主下每会话强制），文件版只留兜底
- 兜底：非 hook 宿主（TRAE Stop 无 transcript、QwenWork 无 hook 事件）由接线 prompt 判断后写入全文版——**不做 hook 感知渲染**（状态同步成本 > 3 行重复收益，违反「显式优于缓存」）

### D3. 本仓 AGENTS.md 手写部分外移

「Team memory fusion」节（~20 行实现入口清单 + 设计约束）移入 `repowiki/wiki/`（实现入口与设计约束文档），AGENTS.md 留一行链接。该节对日常编码会话无用，只对改这块代码的贡献者有用。

### D4. 明确不借

- claude-mem 六事件全采集（SessionEnd + 主动沉淀已覆盖，多事件放大噪音）
- claude-mem 内联 bash 路径解析（我们的相对路径迁移更干净）
- letta commit-on-write（模型相反：我们知识随仓库版本化 + 确知闸门）
- 原生 `async: true`（需真机验证 CodeBuddy 支持，现有 detached 方案已工作，deferred）

### D5. golden fixture 测试（P2，deferred）

仿 teamai-cli 把 `merge_settings_json` 各 IDE 家族渲染输出钉进 golden 测试。本次不做，下次动 `ide_config.py` 前补上。

## 后果

- **正面**：每会话常驻上下文减少 ~100 行；协议单点收敛到 hook 硬通道；细节按需取自 prompt，符合「成本可见性优先」。
- **负面**：非 hook 宿主的 AGENTS.md 兜底文案与 hook 注入存在少量重复（~3 行），接受。
- **迁移**：`_upsert_marked_section` 是标记对标记整块替换（`agents_md.py:139`），存量用户仓库下次运行自动升级，零迁移成本。
- **测试影响**：`test_active_settle_block.py` 断言块内关键词（四判据、每轮禁令、draft 措辞）——D2 只动 `_TASK_MEMORY_AGENTS_SECTION`，不动 `_active_settle_section`，该测试不受影响；`test_task_session_start.py` 断言 hook 注入文案，不受影响。
