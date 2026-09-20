# letta 调研与借鉴分析

> 调研对象：https://github.com/letta-ai/letta
> 基线：2026-09-19 浅克隆 main 分支（letta 与 letta-code 两仓）
> 方法：克隆源码读代码，结论带文件:行号；文档站仅作辅助，冲突时代码优先

## 〇、重要前置发现：仓库结构已变

`letta-ai/letta` 的 main 分支**只是一个 landing page**，其 `AGENTS.md` 明确指出：当前 Letta 的实际实现已迁移到 **`letta-ai/letta-code`**（TypeScript）。只看 letta 仓库会得出完全过时的结论（那里只剩 MemGPT 时代的 Python server 历史与宣传页）。

因此本报告的机制分析全部基于 **letta-code**（`D:\repos\letta-code`，浅克隆 main）。letta-code 是 Letta 的 CLI 编码 agent 产品（对标 Claude Code / Codex CLI），把 Letta 的"stateful agent / memory OS"理念落到了编码场景。

## 一、项目定位

Letta 的核心叙事是 **memory OS**：agent 的价值不在单轮推理，而在跨会话的持久状态。letta-code 是这一叙事的编码场景实现，三大支柱：

1. **Memory Filesystem（MemFS）**——记忆是文件系统，不是向量库；
2. **Reflection（反思）**——后台子代理定期把对话经验蒸馏进记忆；
3. **Recall（回忆）**——专职子代理按需检索记忆注入上下文。

## 二、核心机制（代码事实）

### 2.1 Memory Filesystem：`.letta` 目录即记忆库

- 记忆根目录固定为 `.letta`（`src/agent/memory-filesystem.ts:27` `MEMORY_FS_ROOT = ".letta"`），支持按 agent 划分 scoped 目录（`resolveScopedMemoryDir`，`src/agent/memory-filesystem.ts:98`），可用 `LETTA_MEMORY_DIR`/`MEMORY_DIR`、`LETTA_AGENT_ID` 环境变量覆盖（`src/agent/memory-filesystem.ts:118-123`）。
- 记忆文件是带 frontmatter 的 Markdown（`src/agent/memory-markdown.ts` 的 `parseMemoryFormat`/`renderMemoryMarkdown`），有索引文件概念（`src/agent/memory-format.ts` 的 `isMemoryIndexPath`、`assertMemfsV2MemoryPathIndexed`——写入前强制校验索引已建）。
- 目录树规模集中限幅，env 可覆盖便于测试（`src/utils/directory-limits.ts:16-25`：树最大 500 行/20k 字符、每目录最多 50 子项等，对应 `LETTA_MEMFS_TREE_MAX_LINES` 等环境变量）。

### 2.2 记忆写入：写入即 commit，强制 reason

`memory` 工具（`src/tools/impl/memory.ts`）：

- 六个命令：`str_replace | insert | delete | rename | update_description | create`（`src/tools/impl/memory.ts:33-39`）；
- **`reason` 是必填参数**（`src/tools/impl/memory.ts:43`）——每次记忆变更都要说明动机；
- 写入前 `assertMemoryRepoCleanForWrite` 断言记忆仓库干净，写入后 `commitMemoryWrite`（`src/agent/memory-git.ts:1318`）立即 git 提交，**author 是 agent 身份**（`getAgentIdentity` 用 agentId 拼 git author email，`src/tools/impl/memory.ts:60-80`）——记忆变更历史天然可审计、可归因到具体 agent；
- 另有 `memory-apply-patch.ts` 支持批量补丁式修改；
- 同步模式分 local/remote（`src/tools/impl/memory.ts:55-58`）：本地 backend 直写，云端 backend 走 MemFS sync 到 `api.letta.com`（`src/agent/memory-filesystem.ts:604-636` 有专门的非官方服务器校验）。

### 2.3 Reflection：worktree 隔离的后台反思 + 显式合并策略

这是 letta-code 最有工程含金量的子系统（`src/cli/helpers/reflection-launcher.ts`、`reflection-arena.ts`、`post-turn-reflection.ts`、`src/agent/reflection-runs.ts`）：

**触发**（`src/cli/helpers/memory-reminder.ts`）：

- 默认 **step-count 触发：每 25 个 agent step 反思一次**（`DEFAULT_STEP_COUNT = 25`，`memory-reminder.ts:15`；判定在 `shouldFireStepCountTrigger`，`memory-reminder.ts:236-244`）；
- 另有 post-turn 触发与手动触发；`ReflectionSettings` 含 `trigger / stepCount / merge / mergeInstructions`（`memory-reminder.ts:23-30`）。

**执行**：

- 反思在**独立 git worktree** 中进行（`ReflectionMemoryWorktree`）——子代理对记忆的全部修改都发生在隔离工作树，主记忆库不受污染；
- 反思子代理的 prompt 是 `src/agent/subagents/builtin/reflection-v2.md`，五阶段流程：
  1. **Investigate**（`:62`）——读对话与现有记忆；
  2. **Extract**（`:70`）——提取值得长期保留的经验；
  3. **Update**（`:90`）——改记忆文件（`:94`）；**发现可复用工作流时顺手沉淀为 Skill**（`:108`）；
  4. **Review**（`:156`）——自查改动；
  5. **Commit**（`:176`）——在 worktree 内提交。

**合并**（`finalizeReflectionMemoryWorktreeLaunch`，`src/cli/helpers/reflection-launcher.ts:560-649`）：

- `mergePolicy` 分 **auto / explicit**（`:570`）：auto 在子代理成功后直接合并；explicit 则再派一个 **integration agent** 按用户给的 `mergeInstructions` 审核合并（`:602-617`）；
- 合并失败 → worktree 清理、transcript 保留可重试（`:624-626`），全程遥测（`trackReflectionWorktreeCleanup`，`:640-649`）；
- 子代理成功还会清除"自动反思抑制"标记（`clearAutomaticReflectionSuppression`，`:597-599`）——失败会暂时压制自动反思，避免反复烧钱。

### 2.4 Recall：检索与写入分职

- 专职 recall 子代理（prompt `src/agent/subagents/builtin/recall.md` 与 `src/agent/prompts/recall_subagent.md`）：主 agent 不亲自翻记忆，而是派 recall 子代理去检索（语义检索走 Letta server），把结果摘要带回；
- 配套还有 `history-analyzer-v2`（分析历史对话）、`init-v2`（初始化记忆库）、`fork`（分叉会话）等内置子代理（`src/agent/subagents/builtin/`），由 `src/agent/subagents/manager.ts` 统一管理。

### 2.5 Skills：经验与技能同通道

- 内置技能目录 `src/skills/builtin/`，每个技能一个 `SKILL.md`（如 `managing-shared-memory`、`initializing-memory`、`acquiring-skills`）；
- 技能来源多渠道加载（`src/agent/skill-sources.ts`）；
- 关键设计：**reflection 的 Phase 3 在提取记忆的同时判断是否出现可复用工作流，是则写成新 Skill**（`reflection-v2.md:108`）——记忆（事实/偏好）与技能（流程/方法）由同一次反思产出，不分家。

### 2.6 Mods：可分享的 agent 配置包

`src/mods/` 提供 mods 机制（见其 README）：把 agent 的系统提示、技能、子代理配置打包成可安装/分享的单元，类似"agent 配置的 npm 包"。

## 三、与 CodeWiki 的对照

| 维度 | letta-code | CodeWiki |
|------|-----------|----------|
| 记忆载体 | `.letta` 目录，Markdown+frontmatter，LLM 自由编辑 | repowiki 结构化笔记，工具化写入 |
| 写入闸门 | worktree 隔离 + mergePolicy（auto/explicit） | draft → confirm_note 确认闸门 |
| 蒸馏/反思 | reflection 子代理，step-count/post-turn 触发 | distill_conversation（Mode A/B/C），收尾轮/停顿点触发 |
| 检索 | recall 专职子代理 | query_wiki（工具直查，无子代理） |
| 变更审计 | 写入即 git commit，author=agentId | 笔记落盘进 git，但无强制 commit-on-write |
| 触发粒度 | 25 step / turn 结束 | 自然停顿点判据（4 条） |

两者在"重活异步化、产出先隔离后合并"上高度同构，但 letta-code 的记忆是 **LLM 自主编辑文件**，CodeWiki 是 **确定性工具 + 显式确认**——后者更符合本仓 Doctrine（工具做确定性簿记，推理在调用方）。

## 四、借鉴点（按价值排序，2026-09-20 grill 拷问后更新处置状态）

1. **worktree 隔离 + 显式合并策略** → **excluded**：consolidate_notes 已有 prepare→submit 两段式隔离语义，重造 worktree 层收益存疑。
2. **写入即 commit + 强制 reason** → **absorbed（ADR-0013）**：核对发现 git_sync 已有 auto_stage/auto_push、note_ingest 已有 author 归因，真实缺口只剩 `ingest_note(status="stable")` 直写旁路无强制动机留痕。落地为：`reason` 可选字段进 frontmatter，stable 直写时必填；draft/confirm_note/batch_set_status/add_task_memory 豁免。
3. **step-count 触发节奏** → **excluded**：宿主 IDE 的「轮」与 letta 的 "step" 不同构，计数器无可靠挂载点。
4. **失败压制自动反思** → **excluded（自我修正）**：letta 的压制配合其 25-step 高频触发；本仓触发点天然稀疏（会话开始 + 停顿点各一次），失败率×触发率本就低，加状态位属过度设计。
5. **限额集中管理 + env 覆盖** → **absorbed（ADR-0013，收窄）**：只收敛 task_manager 的压缩阈值组与写入窗口软限进 `limits.py`；不收检索 token 预算与温层注入限额（行为契约文案，Agent 可见性优先）；env 覆盖不借鉴（测试用 fixture 已覆盖）。配套 `lint_wiki` 新增 `threshold_drift` 检查防文案漂移。
6. **记忆与技能同通道沉淀** → **excluded**：蒸馏 submit 已支持 skill_hint + skill_creator 两区制（ADR-0004），无增量。

> 处置定案见 docs/adr/0013-letta-stable-reason-and-limits-module.md；落地顺序 E（limits）先 B（reason）后。

## 五、明确不借鉴什么

- **云端 MemFS 同步**：深度绑定 `api.letta.com`（`memory-filesystem.ts:604-636` 甚至专门校验"非官方服务器即报错"），与 CodeWiki 本地优先、无厂商绑定的前提冲突。
- **LLM 自由编辑记忆文件**：letta-code 的 memory 工具本质是让 LLM 直接 str_replace 记忆文件，无结构校验、无冲突检测。CodeWiki 的结构化笔记 + schema 校验 + 冲突检测（flag_conflict/adjudicate_conflict）是更强的约束，不应放松。
- **遥测埋点体系**：产品化需要，CodeWiki 当前阶段不需要。
- **Mods 分发机制**：解决的是"agent 配置如何分享"的问题，CodeWiki 的 repowiki 本身就在 git 仓库里天然可分享，无需再造。

## 六、结论

letta-code 是"记忆即文件系统 + 反思即后台进程"路线目前最完整的工程实现。对 CodeWiki 最有价值的是**过程工程**而非记忆模型本身：worktree 隔离合并、写入即 commit、step-count 触发、失败压制、限额集中化——这些都是可以直接映射到 CodeWiki 蒸馏/聚合/沉淀管线的确定性改进。记忆模型层面两方路线不同（LLM 自由编辑 vs 结构化工具），保持 CodeWiki 现有路线。
