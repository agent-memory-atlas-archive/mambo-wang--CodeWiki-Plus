# ADR-0013: 吸收 letta 两条——stable 直写强制 reason + 任务记忆限额收敛

- 状态：已接受
- 日期：2026-09-20
- 决策人：用户（grill 拷问定案）
- 关联：docs/letta-调研与借鉴分析.md · ADR-0012（蒸馏层 reason）· ADR-0009（supersede reason）

## 背景

letta-code 调研（docs/letta-调研与借鉴分析.md）识别出 6 个借鉴点，经代码核对与两轮 grill 拷问收敛为 2 个落地项：

1. **写入即 commit + reason 必填**（letta `src/tools/impl/memory.ts:43` reason 必填、`:60-80` author 归因 agentId）。核对发现本仓 `codewiki/src/git_sync.py` 已有 auto_stage/auto_push、`note_ingest.py:396-398` 已有 author 归因（user_id，write-only 不做闸门），真实缺口只剩：`ingest_note(status="stable")` 直写是绕过 confirm 闸门的旁路，无强制动机留痕。
2. **限额集中管理**（letta `src/utils/directory-limits.ts` 单模块 + env 覆盖）。核对发现压缩阈值 40 条/24KB 散落三处：`task_manager.py:195-198`（常量）、`registry.py:2892,2935`（工具描述）、`prompts.py:127,1467`（prompt 文案）。

**明确排除**（候选必有去向，排除必填原因）：

- worktree 隔离合并 → excluded：consolidate_notes 已有 prepare→submit 两段式隔离语义，重造 worktree 层收益存疑；
- step-count 触发 → excluded：宿主 IDE 的「轮」与 letta 的 "step" 不同构，计数器无可靠挂载点；
- 失败压制自动反思 → excluded（**自我修正**，推翻调研报告初判）：letta 的压制配合其 25-step 高频触发，本仓触发点天然稀疏（会话开始 + 停顿点各一次），失败率×触发率本就低，加状态位属过度设计；
- 记忆与技能同通道沉淀 → excluded：蒸馏 submit 已支持 skill_hint + skill_creator 两区制（ADR-0004），无增量；
- env 覆盖限额 → excluded：本仓测试用 fixture 覆盖，无 letta 的测试便利痛点。

## 决策

1. **B2（方案 B 修订）：`ingest_note` 新增可选 `reason` 字段**，写进 frontmatter `metadata.reason`；**当 `status="stable"` 时必填**，缺失即 schema 校验拒绝（错误信息提示补 reason 或改走 draft→confirm）。**能力边界声明：reason 是意图声明，不是验证机制**——它由调用方 Agent 自报，schema 只能保证「填了」不能保证「是真的」；其价值在可见性（旁路留痕）、摩擦（绕闸门前须显式说出理由）、可归因（出错时追责链完整），不在真实性。豁免边界：
   - draft 豁免——有 confirm 闸门兜底，且 ADR-0012 已在蒸馏 prompt 层要求每条 note 自带 rationale；
   - `confirm_note` / `batch_set_status` 豁免——人工审核动作，`by` 字段已留痕；
   - `add_task_memory` 豁免——高频直写通道（ADR-0002），加必填违背停顿点即写即沉淀初衷。
2. **B2 配套：`evidence` 可选字段**（结构化锚点：`test_ref` / `commit_ref` / `reviewed_by`），复用 `confirm_note` 既有语义——提供 evidence 时记录 `metadata.verification` 并升 `confidence_level=strong`。reason 管可见性（防静默），evidence 管验证（防编造）：evidence 是**人工可核验的**（commit hash 是否存在、测试是否如所述，人可以查），与自由文本 reason 分工明确。
3. **E1+E7：新建 `codewiki/mcp/tools/limits.py`**，收敛 `task_manager.py` 的压缩阈值组（`_COMPACTION_THRESHOLD_COUNT=40` / `_COMPACTION_THRESHOLD_BYTES=24*1024` / `_COMPACTION_KEEP=20` / `_COMPACTION_SUMMARY_MAX_CHARS=4096`）与写入窗口软限（`_WRITE_WINDOW_SOFT_LIMIT=5`）；task_manager 改为从 limits.py import。**不收**检索 token 预算与温层注入限额——它们是行为契约文案（Agent 可见性优先），不是实现常量。
4. **lint_wiki 新增 `threshold_drift` 检查**：正则扫描 registry.py / prompts.py 文案中的阈值数字（40 / 24KB / 20 / 4096 / 5），与 limits.py 常量比对，不一致即 warn。文案中其他数字（如温层 2 条、max_memories 20/5）进白名单不检查。
5. **顺序：E 先 B 后**——E 会动 registry.py 的 compact 描述文案，B 动 registry.py 的 ingest_note schema，先 E 后 B 避免同文件并行冲突。
6. 与 ADR-0012 的关系：0012 管**蒸馏产物**的 rationale（prompt 层，LLM 自律，产物过确认闸门）；本 ADR 管**直写 stable** 的 reason（schema 层，工具强制）——两层互补不重叠，蒸馏管线不改。

## 后果

- 正面：stable 直写旁路补上审计缺口（谁写的、为什么可信，两问都有答案）；阈值漂移有 lint 兜底；改动面小（一个新模块 + 两个字段 + 一个 lint 检查）。
- 负面/代价：`threshold_drift` 正则匹配文案数字需维护白名单，文案新增数字时可能误报；stable 直写多一步填 reason 的成本（接受——这正是设计意图）；reason 可被 Agent 编造（接受——能力边界已声明，验证职责由 evidence 承担）。
- 测试：ingest_note stable 缺 reason 拒绝的用例；limits.py 常量与 task_manager 行为等价的回归；threshold_drift lint 用例（含白名单）。

## 复核

- letta 的 reason 必填是全局的（所有记忆写入），本 ADR 收窄到 stable 直写旁路——收窄依据是本仓已有 confirm 闸门覆盖 draft 路径，letta 没有等价闸门所以必须全局强制；
- 失败压制的排除是本轮 grill 的自我修正：调研报告 §四.4 的初判（「可加一层」）被「触发频率不同构」证伪，报告已同步改写。
