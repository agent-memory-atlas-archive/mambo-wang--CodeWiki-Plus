<!-- CodeWiki LLM Wiki -->

## CodeWiki LLM Wiki

本项目已使用 [CodeWiki](https://github.com/mambo-wang/CodeWiki-Plus) 生成 LLM Wiki 文档，位于 `repowiki/` 目录。

**入口文件：**

- [`repowiki/wiki/overview.md`](repowiki/wiki/overview.md) — 仓库级架构总览（含 Mermaid 架构图）
- [`repowiki/wiki/index.md`](repowiki/wiki/index.md) — 文档目录与知识笔记索引
- [`repowiki/schema.yaml`](repowiki/schema.yaml) — 项目文档约定（命名规范、必填章节等）

### 使用建议

1. **编码前**：先用 `query_wiki` 搜索相关模块文档，了解架构约定和依赖关系
2. **做决策时**：用 `query_wiki` 搜索已有的 `decision` 类型笔记，避免重复讨论
3. **完成重要决策后**：用 `ingest_note` 归档，让未来的 Agent 和团队成员都能查到
4. **定期维护**：用 `lint_wiki` 检查文档是否过时，保持文档与代码同步

### 回答时显式标注依据

回答涉及本仓库的知识或代码时，在**关键论断处直接标注来源**，不要只写"根据文档/代码"却不给名字：

- 引用 `query_wiki` 检索到的文档/笔记 → 标注 `（依据：<file>）`，`<file>` 必须与检索结果返回的 `file` 字段完全一致；
- 引用代码事实 → 标注 `<代码文件>:<行号>`，行号以你实际读取代码所见为准，不要照抄文档里可能已过时的行号；
- 依据来自本次代码核对而非文档 → 明说来源，如 `依据本次代码核对：<代码文件>:<行号>`。

正文标注是给人读的溯源承诺；行尾的 `codewiki:referenced-docs` 注释是机器采纳信号，两者并存。

### 采纳声明（检索反馈）

通过 `query_wiki` 检索并**实际使用了**某条结果时，在最终回复末尾附带：

```
<!-- codewiki:referenced-docs: ["notes/pitfall-xxx.md", "wiki/modules/yyy.md"] -->
```

路径必须与 query_wiki 返回的 `file` 字段完全一致。声明过的文档获得采纳计数，未来检索排序提升；长期高频召回却零采纳的笔记会被 `lint_wiki` 的 `low_adoption` 检查标记。只声明真正用到的文档——漏报可容忍，误报不可容忍。

### 纠正识别与经验沉淀

被用户纠正、吐槽或补充了未知上下文时，执行三步流程：

1. **反思**：明确说出错在哪里、正确做法、根因；
2. **起草笔记**：结构化内容（背景→正确做法→根因分析）；
3. **征求确认**：展示草稿询问"要把这条经验记录到 Wiki 吗？"——**必须确认后才执行 `ingest_note`**，不要默默保存。

纠正信号：明确否定（"不对""你搞错了"）、重复犯错的不满（"又…""上次就…"）、改后仍不满意、补充关键上下文（"这个项目一直都是…"）、指出命名与实际行为不一致。

只记录有复用价值的经验——未来 Agent 或新同事遇到同样场景有用的才记；临时调整、个人偏好不记。

**归档示例：**

```json
{
  "note_type": "lesson",
  "title": "OrderService.process() 只做参数校验不做业务处理",
  "content": "## 背景\n\nAgent 误以为 OrderService.process() 包含完整业务逻辑，基于方法名做了错误的设计假设。\n\n## 正确做法\n\nprocess() 仅做入参校验和格式化，实际业务处理在 OrderService.execute() 中。老项目方法名与实际行为不一致是常见情况，应优先阅读实现而非信任方法名。\n\n## 根因\n\n十几年老项目，方法经过多次重构但名称未更新。",
  "related_modules": ["order"]
}
```

### 主动知识沉淀

不要等用户纠正才记录。触发信号（任一）：多步骤调试定位根因、多方案讨论后做出选择、代码行为与文档/命名不一致、用户补充隐性项目知识、调研收敛到明确结论、发现可复用模式。

**四问过滤（全部通过才记录）：** 下次对话还能用到？其他 Agent/新同事能直接受益？`query_wiki` 确认未覆盖？属于"事实/决策/模式/教训"而非临时状态？

**路由表：**

| 知识类型 | 写入方式 |
|---------|---------|
| 技术选型/方案取舍 | `ingest_note(note_type="decision")` |
| 踩坑/易错点 | `ingest_note(note_type="pitfall")` |
| 经验教训 | `ingest_note(note_type="lesson")` |
| 架构事实发现 | `ingest_note(note_type="architecture")` |
| 临时绕过方案（含恢复条件） | `ingest_note(note_type="workaround")` |
| 多方案横向对比 | `write_doc_file(page_type="comparison")` |
| 调研结论存档 | `write_doc_file(page_type="query")` |

执行：提取候选 → 四问过滤 → `query_wiki` 查重 → 起草结构化内容（背景→结论→根因→适用范围）→ **展示草稿征求确认后才写入**。多个候选项在自然停顿点统一呈现，避免频繁打断。

不要记录：本次任务临时变量/路径/参数、用户个人偏好、代码注释或 README 已写明的信息、未经验证的猜测。

### 产出语言（语言闸门）

所有产出使用**中文**——Wiki 文档、笔记、代码注释、commit message、给用户的回复，除非用户明确要求其他语言。检索到的历史文档若为其他语言，新产出仍按本规则。

<!-- /CodeWiki LLM Wiki -->

## Agent skills

### Issue tracker

Issues live in this repo's GitHub Issues (uses the `gh` CLI). See `docs/agents/issue-tracker.md`.

### Triage labels

Five canonical roles: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout: root `CONTEXT.md` + `docs/adr/`. See `docs/agents/domain.md`.

## Team memory fusion (conversation → Wiki)

借鉴 Team-Agent-Memory 的"从对话中提取可检索经验"能力,融合进 CodeWiki 知识飞轮。

**实现入口：**
- `codewiki/mcp/tools/knowledge_loop.py` — `capture_conversation` 工具(采集对话到 `repowiki/raw/`)
- `codewiki/mcp/tools/distill_conversation.py` — `distill_conversation` 工具(蒸馏 raw → 结构化知识)
- `codewiki/mcp/_ide_hook.py` — IDE hook 采集脚本(默认关,`--enable` 或环境变量开启)
- `repowiki/team-memory-hook.md` — Hook 接线文档与配置说明
- `repowiki/ontology.yaml` — 本体论术语表模板(可选,增强检索)
- MCP prompt `team-memory-hook`（prompts/list）— 启用/关闭采集 hook 的操作指引
- MCP prompt `distill-conversations`（prompts/list）— 蒸馏工作流指引(prepare → 提取 → submit → 评审)

**关键设计约束(实现时务必遵守)：**
- `distill_conversation` 是**无状态**工具,自身不持有 LLM;LLM 由调用方提供。三种模式:**Mode A**(subagent 注入 `llm` async 回调,内联)、**Mode B**(`run_in_background=true`,从 `MAIN_MODEL`/`LLM_BASE_URL` 环境变量构建)、**Mode C**(IDE Agent 自己当 LLM:`mode="prepare"` 取 transcript+system prompt → Agent 提取 → `mode="submit"` 交回 `distilled` JSON,纯 MCP JSON 可走)。蒸馏是 LLM 重活,必须异步/后台执行,不阻塞主线程。
- 自动采集 IDE hook(可选,默认关)**只落 raw,不蒸馏**;蒸馏需显式调用 `distill_conversation`,永不自动发生。
- `repowiki/raw/` 是**暂存区,不进 `query_wiki` 检索**,蒸馏完成后由 `distill_conversation` 删除(除非 `keep_raw`);未蒸馏的 raw 会一直保留(无自动过期);不膨胀、不影响查询性能。
- 蒸馏产出 `status=draft` 的 note,须 `confirm_note` 确认后才成正式知识。
- 触发形态:**both** —— 手动命令(主) + IDE hook(可选)。
- **Mode C submit 走 `distilled_file` 文件侧通道(勿内联大 JSON)**：多条大对话蒸馏时,`distilled` 内联参数可能超出 MCP 传输限制导致失败。正确做法:先用 `write_to_file` 把蒸馏 JSON(形状 `{conversation_id: {notes, memories}}`,或单条裸 `{notes, memories}` 配合 `conversation_id` 参数)写入 `repowiki/raw/.distill-*.json`,再 `distill_conversation(mode="submit", distilled_file=<路径>)` 只传小路径;相对路径先按推导出的 repowiki 目录再按 CWD 解析。小载荷仍可内联 `distilled`(两者可合并,内联优先)。**不要再写临时 Python 脚本调用 handler 绕过**。

<!-- TEAM-MEMORY-TASK:START -->
## Task memory (任务记忆)

跨会话延续长线工作上下文。任务记忆是**任务范围内的进度知识**（本次做了什么、下一步、待办），与 Wiki 笔记（**跨任务的通用经验**）互补。

**会话开始时（必须执行）：**
1. `list_tasks(status="active")` 列出进行中的任务
2. **必须用 `ask_followup_question` 弹框，且只弹一次、一框列全**：只调用 1 次，questions 数组只放 1 个 question（标题「任务关联」，multiSelect=false），options 一次性列出「每个进行中任务」+「新建任务…（在输入框直接输入名称）」+「跳过」。**严禁**因工具 schema 建议 2-4 个 options 就拆成多个 question 或分多次弹框；唯一例外是用户选了「新建任务…」却没给名字，可再弹一次要名字
3. 用 `set_session_task(source_session_id=<会话id>, task_id=<任务id>)` 绑定；列表里没有的任务名先 `create_task(title=<任务名>)` 再绑定；用户选「跳过」则本次不关联
4. `get_task_context(task_id=<选中任务>)` 拉取任务描述 + 记忆 + 关联笔记
5. `pending_raw_count > 0` 时**异步补蒸馏**：发一个异步 subagent（后台执行，不阻塞回答）补蒸馏，**清空本任务的全部待蒸馏积压**（不设条数上限）；补蒸馏只提取经验笔记（skip_memories 默认生效，ADR-0010 通道互斥），任务记忆由主动沉淀通道直写；主 Agent 直接回答用户提问，在自然停顿点重新 `get_task_context` 拉取最新记忆、展示待确认草稿。subagent 失败/超时不重试——未蒸馏的 raw 留在 raw/ 等下次会话再补。蒸馏产出的草稿笔记须 `confirm_note` 确认后才落盘；任务记忆直写、无需确认（ADR-0002）
6. **项目定向（按条件执行）**：若本会话上下文中**没有**已注入的 Team Doctrine / 知识库概览，调用 `query_wiki(mode="overview")` 拉取一次；已注入则跳过，绝不重复拉取
7. **会话收尾（按条件执行）**：本文件存在 CODEWIKI-ACTIVE-SETTLE 块 → 按该块执行（停顿点直写沉淀），跳过下方传统采集；不存在 → 按下方**传统收尾轮采集**执行

**传统收尾轮采集（任务完成 / 用户道别 / 用户显式要求记录时）：**
将本会话对话重建为 `[{role, content}]` 列表，调用 `capture_conversation(conversation=..., source_session_id=<本会话id>, task_id=<任务id>)` 落 raw。**user 消息必须逐字保留**，assistant 保留关键结论原句，工具调用略去。同一会话多次收尾采集会被 supersede 替换，不会堆积。

完整工作流与实现约束见 MCP prompt：`get_prompt(name="task-workflow")` —— 按需获取。
<!-- TEAM-MEMORY-TASK:END -->

<!-- CODEWIKI-ACTIVE-SETTLE:START -->
### 主动沉淀协议（自然停顿点即写即沉淀）

与批处理（收尾采集 → 下轮蒸馏）互补：停顿点即写即沉淀，任务记忆与草稿笔记下一轮 `get_task_context` 即可见，不必等蒸馏。

**① 自然停顿点判据（命中任一即沉淀；每轮回复收尾前自查，不要依赖「想起来」）：**
1. 任务里程碑达成；
2. 关键技术决策落定，或澄清/纠偏了产品机制、代码事实等关键认知；
3. 用户话题明显转向；
4. 收尾轮（强制兜底，必做）——无论会话中是否命中前三条，收尾轮必须做一次沉淀自查：本会话是否有未沉淀的进展/决策？有则按下方两条路径补写。

**不做字面每轮沉淀**：任务记忆追加无去重，每轮都写会灌爆记忆并反复触发 40 条/24KB 压缩阈值——只在停顿点沉淀。**宿主 IDE 自带的工作记忆（如 `.codebuddy/memory/`）与本协议的任务记忆是独立通道**，写了前者不豁免后者。

**两条写入路径（均当轮落盘，下一轮 `get_task_context` 即取；禁止手写文件）：**
- 任务记忆：`add_task_memory(task_id=<绑定的任务id>, content="本段进展/决策/下一步")` 直写——无需确认（ADR-0002）。写入标准（ADR-0009）：只记会改变下一步行动的进展/决策/约束；推翻旧记忆时传 `supersedes=<旧条目id>`，不要追加平行副本；近重复写入会被拒绝（difflib > 0.85），改用 supersedes 或合并改写后重试；
- 通用经验：`ingest_note(status="draft", ...)` 落草稿——**确认闸门保留**：草稿笔记须经 `confirm_note` 确认后才进入全局检索语料，不得跳过确认。草稿落盘即可被下一轮 `get_task_context` 的 `related_notes` 以 `status: draft` 展示、能确认、能参与冲突检测。
<!-- CODEWIKI-ACTIVE-SETTLE:END -->
