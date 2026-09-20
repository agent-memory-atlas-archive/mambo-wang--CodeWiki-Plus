# Team memory fusion（对话 → Wiki 实现入口）

> 从根 AGENTS.md 外移（ADR-0015）：本页只对改这块代码的贡献者有用，日常编码会话无需加载。

借鉴 Team-Agent-Memory 的"从对话中提取可检索经验"能力，融合进 CodeWiki 知识飞轮。

## 实现入口

- `codewiki/mcp/tools/knowledge_loop.py` — `capture_conversation` 工具（采集对话到 `repowiki/raw/`）
- `codewiki/mcp/tools/distill_conversation.py` — `distill_conversation` 工具（蒸馏 raw → 结构化知识）
- `codewiki/mcp/_ide_hook.py` — IDE hook 采集脚本（默认关，`--enable` 或环境变量开启）
- `repowiki/team-memory-hook.md` — Hook 接线文档与配置说明
- `repowiki/ontology.yaml` — 本体论术语表模板（可选，增强检索）
- MCP prompt `team-memory-hook`（prompts/list）— 启用/关闭采集 hook 的操作指引
- MCP prompt `distill-conversations`（prompts/list）— 蒸馏工作流指引（prepare → 提取 → submit → 评审）

## 关键设计约束（实现时务必遵守）

- `distill_conversation` 是**无状态**工具，自身不持有 LLM；LLM 由调用方提供。三种模式：**Mode A**（subagent 注入 `llm` async 回调，内联）、**Mode B**（`run_in_background=true`，从 `MAIN_MODEL`/`LLM_BASE_URL` 环境变量构建）、**Mode C**（IDE Agent 自己当 LLM：`mode="prepare"` 取 transcript+system prompt → Agent 提取 → `mode="submit"` 交回 `distilled` JSON，纯 MCP JSON 可走）。蒸馏是 LLM 重活，必须异步/后台执行，不阻塞主线程。
- 自动采集 IDE hook（可选，默认关）**只落 raw，不蒸馏**；蒸馏需显式调用 `distill_conversation`，永不自动发生。
- `repowiki/raw/` 是**暂存区，不进 `query_wiki` 检索**，蒸馏完成后由 `distill_conversation` 删除（除非 `keep_raw`）；未蒸馏的 raw 会一直保留（无自动过期）；不膨胀、不影响查询性能。
- 蒸馏产出 `status=draft` 的 note，须 `confirm_note` 确认后才成正式知识。
- 触发形态：**both** —— 手动命令（主） + IDE hook（可选）。
- **Mode C submit 走 `distilled_file` 文件侧通道（勿内联大 JSON）**：多条大对话蒸馏时，`distilled` 内联参数可能超出 MCP 传输限制导致失败。正确做法：先用 `write_to_file` 把蒸馏 JSON（形状 `{conversation_id: {notes, memories}}`，或单条裸 `{notes, memories}` 配合 `conversation_id` 参数）写入 `repowiki/raw/.distill-*.json`，再 `distill_conversation(mode="submit", distilled_file=<路径>)` 只传小路径；相对路径先按推导出的 repowiki 目录再按 CWD 解析。小载荷仍可内联 `distilled`（两者可合并，内联优先）。**不要再写临时 Python 脚本调用 handler 绕过**。
