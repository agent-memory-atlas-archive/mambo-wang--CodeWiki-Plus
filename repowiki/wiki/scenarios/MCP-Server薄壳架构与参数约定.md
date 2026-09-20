---
type: Scenario
title: MCP-Server薄壳架构与参数约定
description: 薄壳分层与隐式 session_id、output_dir 恒为 repo_path 纯函数、E2E 显式传路径、检索预算口径与 check
tags:
- CodeWiki-CN
generated:
  by: codewiki/5.8.0
  at: '2026-09-08 05:54:38+00:00'
stale_after: '2026-12-07'
aliases:
- MCP-Server薄壳架构与参数约定
status: stable
metadata:
  generated_from: f08feab
  resource: repo://CodeWiki-CN
  code_fingerprint: sha256:829467a7f49459ddf16d1711753a335b7338eb7409360e8d30565d9f78d11621
  source_notes:
  - notes/2026-09-07-mcp-server-子进程-cwd-固定为启动目录oschdir-不影响e2e-测试必须显式传-workspace-p.md
  - notes/2026-09-07-output-dir-是-repo-path-的纯函数写路径一律布局推导砍跨进程持久化只读检索保留跨仓寻址出口.md
  - notes/2026-09-07-serverpy-硬编码-version-与-pyproject-漂移mcp-initialize-返回版本误导客户端.md
  - notes/2026-09-05-query-wiki-p0-改进四项定案rev2-评审定稿est-tokens-by-file-v1-仅-notes-新.md
  - notes/2026-09-05-query-wiki-的-check-模式是轻量预检不计入检索统计不污染-usageheat-排序信号工作流若不内建到工.md
  - notes/2026-09-05-检索预算口径打架前门-1200-字符-snippet-300-10-条只-4-条带内容expand-后门-1020000.md
  - notes/2026-08-03-mcp-工具-schema-不声明-session-idhandler-隐式读取.md
  - notes/2026-08-25-doctrine-不会自动注入-agent-上下文唯一通道是-query-wikimodeoverview.md
  - notes/2026-08-26-handle-query-wiki-在-session-存在时每次查询都全量重建检索索引.md
  - notes/2026-08-29-引用已有笔记前须检查其-statusdeprecated-笔记不应被采纳.md
  - notes/2026-09-05-code-routing-代码注入分档的真实规则纯-boilerplate-文件仅签名businessinfra混合全量.md
  - notes/2026-09-05-confirmreject-生命周期已从-knowledge-looppy-拆到-note-lifecyclepy202.md
  - notes/2026-09-07-i18n-语言来源优先级configjson-lang-codewiki-lang-env-系统-locale-zh且不.md
  - notes/2026-09-07-mcp-promptslist-与-promptsget-无语言协商参数语言只能在-server-进程启动时确定.md
  - notes/2026-09-07-mcp-层中文返回文本-i18n-方案定案yaml-双文件全量一次性全做.md
  - notes/2026-09-07-prompt-正文是逻辑模板混合体不能整块搬进-yaml-语料.md
  - notes/2026-09-07-server-在-serverpy-模块顶层构造语言初始化必须早于它.md
  - notes/2026-09-07-存量中文落盘产物不追溯重写语言策略只作用于新生成整体重写路径.md
  summary: 补入 MCP 层 i18n 定案（语言优先级/启动期确定/存量不追溯）、code_routing 两档真实规则、note_lifecycle
    拆分、deprecated 笔记引用前查 status
  heat: 5
  confidence_level: weak
---
## 工作场景
codewiki/mcp/ 的架构分层、工具参数面与检索契约。适用于新增/修改 MCP 工具、重构 server 层、排查参数与路径解析、调检索成本与排序信号、写协议层 E2E 测试。

## 适用条件
开发新工具、改 output_dir/session 解析、agent 侧调用本项目 MCP、排查检索/注入问题、预算与排序信号调优。

## 核心 SOP
1. 新增工具只动两处：`tools/<x>.py` 实现 handler + `registry.py` 注册 schema 与 handler_path；server.py 只留 list_tools/call_tool/main。
2. session_id 是隐式参数：inputSchema 不声明，handler 内 `arguments.get("session_id")` 读取。
3. 改 schema 前先分清校验层：`required` 是 MCP 层校验、先于 handler 执行，放宽必填必须改 registry 的 required——不要效仿「schema 未声明却在 handler 读」的既有先例（repo_path、origin_filter）。
4. agent 侧调用先读工具描述确认参数名（如 get_prompt 是 `prompt_type` 不是 name）。
5. 同一约定写两处：MCP prompt（常驻注入）+ AGENTS.md（按需可查），改约定同步两处。
6. 写测试/smoke 不碰真实仓库：用隔离仓库路径避免污染 `.codewiki/analysis_cache.db`。
7. doctrine 不自动注入：主通道是 `query_wiki(mode='overview')`（截断 1300 字符），SessionStart hook 的 `_load_doctrine` 是补强；AGENTS.md 是软约束，与任务提示竞争时常落败。
8. `handle_query_wiki` 在 session 存在时每次查询全量重建索引（DELETE 三表且无锁）——评审卡顿根因；并行化需「预热一次索引 → 查询走 skip_index_build → 再并行 collector」。
9. 配置加载函数对 YAML 损坏必须 `logger.warning`（带文件路径与异常），不可静默回退 None。
10. **output_dir 恒为 repo_path 的纯函数**：写路径一律 `default_output_dir(repo_path)` 布局推导，显式 output_dir 降级为 legacy 并告警忽略；砍掉 `cache.repo_meta.output_dir` 跨进程持久化（事故源：跨仓 output_dir 劫持 session 清空真实索引）。唯一例外是无宿主仓的孤立 wiki 目录。
11. **E2E 测 MCP server 必须显式传 `workspace_path`/`repo_path`**：子进程 cwd 固定为启动目录，测试进程 `os.chdir` 对子进程无效；跑完按生成物清单核对落点并 `git status` 复核。
12. **检索成本口径要互相可推导**：前门注入预算 1200 字符 ÷ snippet 300 = 10 条只 4 条带内容，后门 expand 上限 20000 ×10 ≈ 5 万 token；先给调用方 `est_tokens` 让展开代价可见，再引导按需展开。
13. **先 check 后检索**：`query_wiki(mode=check)` 不记检索统计、不污染 usage/heat 排序信号；模式选择要内建进工具描述（AGENTS.md 软约束常被读不到）。
14. 提示字段沿用 `*_hint` 家族命名（全仓无 advice 先例）。
15. **MCP 层 i18n**：语言优先级 `~/.codewiki/config.json` 的 `lang` > `CODEWIKI_LANG` env > 系统 locale > 兜底 zh；语言源不放项目级 schema.yaml。MCP 协议（prompts/list、prompts/get）无语言协商参数，语言只能在 server 进程启动时确定；`Server(...)` 在 server.py 模块顶层构造，语言初始化必须早于它。方案定案：YAML 双文件（zh/en）全量、一次性做；prompt 正文是「逻辑+模板」混合体（条件分支、运行时占位符），不能整块搬进 YAML。存量中文落盘产物不追溯重写，语言只作用于新生成/整体重写路径；schema.yaml 已存在绝不动。
16. **引用 query_wiki 返回的笔记前先查 status**：deprecated 表示方案已被否决/取代，不可作为行动依据；仅 draft/confirmed 可采纳。
17. **code_routing 代码注入分档是文件粒度两档，非传闻三档**：纯 boilerplate 文件（file_categories == {"boilerplate"}）仅签名（≤15 参数）；business/infra/混合文件整文件全量；1-hop 依赖仅签名。「infra 摘要」档不存在（prompt_template.py:596-659）。
18. **confirm/reject 生命周期实现已拆到 note_lifecycle.py**（2026-09 重构）：knowledge_loop.py 仅 2.4KB 兼容门面；handle_confirm_note 在 note_lifecycle.py:56-91（draft→stable、append verified、续期 stale_after）。找实现别去 knowledge_loop.py。
19. **i18n 接线点若在模块级，语言会在 import 期被固化**：`Server(...)` 与 `_register_prompts(server)` 均为模块级，语言初始化必须放在 Server 构造之前；任何在模块级求值的中文字面量都会在 import 那一刻被定死。
20. **Windows 上 locale.getlocale() 返回英文语言名而非 ISO 代码**：中文系统会被误判成英文（返回 'Chinese (...)' 而非 'zh_CN'）；语言判定须显式映射或用其他 API。
21. **双语语料与模板一致性两类静默故障**：命名空间错位（语料插错组，`t()` 对缺失 key 返回带前缀哨兵不抛错，默认中文路径下照样渲染，单看结果不易察觉）；英文版 YAML 半角冒号（值内含 `:` 会被解析器吃掉）。

## 判断逻辑
- dispatch() 已有统一异常兜底，handler 内抛异常是安全契约。
- 索引重建触发条件过宽（session 存在即重建），应复用 freshness 判断。
- 成本可见性优先于新造能力：让已有设计真正生效，比加参数更划算。
- 兼容性约束要提前点名：给输出加字段会打破精确断言字段集的测试。

## 禁忌与反模式
- 不在 inputSchema 声明 session_id；不复制 `_resolve_output_dir` 到各工具。
- 不绕过 dispatch 直接 import handler 组装参数。
- 不在 server.py 手写版本号（从 `codewiki.__version__` 注入；发版核查四处）。
- 不把「只读工具保留显式 output_dir」当逃生门（已全部移除）。
- 不让预算参数（snippet 长度/结果条数/expand 上限）各自拍脑袋。

## 关键事实依据
- registry.py 约 85% 是 schema（改一工具跳两处，已知成本）。
- output_dir 收敛落地：f09b7d1（45 文件）+ e6df9f7（测试 31 文件）+ 319f10d。
- check 模式不记检索统计是显式设计（knowledge_loop.py 注释），普通检索当预检会稀释真实信号。