# memos 调研与借鉴分析

> 调研日期：2026-09-19 · 任务：他山之石 · 方法：克隆源码读代码（D:\repos\memos，HEAD 7e3d3c6，2026-09-19，v0.31.0-rc.2-16-g7e3d3c6），结论均经代码核对，非文档站口径。

## 1. 项目概况

| 维度 | 事实 |
|------|------|
| 定位 | 自托管、隐私优先的轻量笔记应用（"Memos"），单二进制部署，多用户 + 空间（Spaces）协作 |
| 技术栈 | Go 后端（Echo v5 + grpc-gateway + protobuf 单一定义源）+ React/TS 前端，MIT |
| 活跃度 | 40k+ star，提交极活跃（HEAD 为调研当日），v0.31.0-rc.2 之后 16 个提交 |
| 存储 | SQLite/MySQL/Postgres 三方言，`store/driver.go:10-80` 按聚合（Memo/Space/Attachment/User…）声明 Driver 接口 |
| 查询 | `filter/` 包：CEL 表达式 → IR → 方言 SQL 编译器（filter/README.md:1-32） |
| AI | 仅音频转写（OpenAI STT / Gemini audio-LLM），provider 配置存实例设置（server/api/v1/ai_service.go:49-100） |
| MCP | `server/mcp/`：OpenAPI 驱动、进程内回环调用 REST API 的 Streamable HTTP MCP server（server/mcp/README.md:3-14） |

领域上 memos 是笔记应用、本仓是代码知识库，业务面无重叠；但其 **MCP server 工程化程度是迄今调研项目里最高的**，多个机制直接击中本仓 MCP 层的现状缺口。

## 2. 核心机制（代码核对）

### 2.1 OpenAPI 驱动的工具目录：单一事实源 + 策展白名单
- 所有工具从生成的 `proto/gen/openapi.yaml` 派生，MCP 包不自持任何业务逻辑（server/mcp/README.md:8-14）。
- `curatedOperationIDs` 白名单选 36 个操作（catalog.go:12-54），`buildCuratedTools` 对缺失 ID / 重名 fail-fast（catalog.go:179-201）。
- 命名规则机械化：`MemoService_ListMemos → memo_list_memos`（catalog.go:231-238）。
- 覆盖表（schema 放宽/收紧、annotations 修正）引用不存在的 operation 时启动即报错——**防"静默失配"**（catalog.go:152-169）。

### 2.2 进程内回环执行：工具调用 = 一次内部 HTTP 请求
- `apiAdapter.execute` 把工具参数拼成 `/api/v1/...` 请求，用 `httptest.ResponseRecorder` 打到同一个 Echo server（adapter.go:30-47）。
- 收益：鉴权/限流/校验全部复用 REST API 原样，MCP 层零重复逻辑；OpenAPI 既是 API 文档又是工具 schema 源。
- 细节讲究：把 `/mcp` 请求上下文里已解析的真实客户端地址设为内部请求的 peer，避免所有匿名 MCP 调用共享 `httptest` 占位地址（192.0.2.1）导致限流桶合并（adapter.go:87-98）。

### 2.3 工具 annotations：HTTP 方法推导 + 逐操作修正
- 基线按方法推导：GET→readOnly+idempotent，DELETE→destructive+idempotent，其余→皆 false（catalog.go:383-401）。
- 方法启发式错的地方用覆盖表修正：`SetMemoAttachments`/`SetMemoRelations` 是 PATCH 但整体替换集合，标 idempotent+destructive；`UpdateMemo`/`UpdateSpace` 覆写既有字段也标 destructive（server/mcp/README.md:221-228）。
- `OpenWorldHint` 全部 false；注释明确"annotations 是客户端提示，不替代 API 鉴权"（server/mcp/README.md:230-231）。

### 2.4 结果形状：structuredContent 规范化 + 错误不带 schema
- 成功结果强制对象形：对象原样、空响应→`{"ok":true}`、裸数组→`{"result":[...]}`、标量→`{"result":v}`（result.go:11-36）——修复 strict 客户端拒绝裸数组的 #6022。
- 错误结果只走 `IsError: true` + 文本，**不带 structuredContent**——因为每个工具都声明了 outputSchema，strict 客户端会拿错误载荷去对成功 schema 校验，反而掩盖真实错误（result.go:38-50）。
- 连 grpc-gateway 序列化器都为 MCP 契约定制：未设字段输出 `null` 会挂掉 outputSchema 校验，故换装 omit-null 的 marshaler（修复 #6139，server/mcp/README.md:244-251）。

### 2.5 任务级 MCP eval：测"LLM 能不能用工具完成任务"
- 单测只验管道（schema/命名/annotations），eval 测真正要紧的事：**LLM 组合工具能否答对真实问题**——是工具描述与可发现性的回归网（evals/README.md:3-8）。
- 15 个问答对钉在确定性种子数据上（4 用户/31 memos/35 reactions/4 spaces），相对时间戳保证跨次重播稳定；明确警告公共 demo 数据已漂移不可用（evals/README.md:16-41）。
- 每题独立、只读、需多次工具调用、答案可字符串比较（memos_eval.xml:22-62）。

### 2.6 其他
- Schema 解析：OpenAPI `$ref` 顶层内联、嵌套转 `$defs`、递归组件用占位种子 + resolving 集合防环（server/mcp/README.md:72-101）。
- 双层入参校验：手写结构检查出友好报错 + `google/jsonschema-go` 做规范兜底（validation.go:12-39）。
- 静态目录 TTL：目录启动后不变，不广告 `listChanged`，`tools/list`/`server/discover` 打 24h `ttlMs`，避免客户端空挂通知流（service.go:26-29, 101-119）。
- CEL→SQL 三段式编译器（parse→IR→render，方言差异全封装在 renderer），`now` 每次编译冻结一次（filter/README.md:1-32）。
- Markdown `#tag` 用 goldmark AST transformer 在 GFM 解析后跑，白名单透明容器内才替换，raw text 不动（markdown/extensions/tag.go:21-91）。

## 3. 与本仓对照处置表

| # | memos 机制 | 本仓现状（代码核对） | 处置 |
|---|-----------|---------------------|------|
| 1 | 工具 annotations（readOnly/destructive/idempotent hint + 方法推导 + 覆盖表） | `ToolDef` 仅 schema/handler_path/mode/takes_store（registry.py:44-51）；所有 `Tool(` 只有 name/description/inputSchema（registry.py:106-155），全仓无 annotations | **absorbed（挂起搭车，2026-09-19 grill 轮裁决）**：SDK 层已支持（`mcp/types.py:1329` `Tool.annotations: ToolAnnotations`），改动方向确定但**不单独立项**——等下次 registry 契约变更时顺路落地。判定标准采用 memos「覆盖/删除既有状态 → destructive；纯新建 → 非 destructive」：destructive 集合 = {edit_doc_file, reject_note, delete_task}，confirm_note/ingest_note/batch_set_status 不标（宁严勿松会让警告泛滥失去信号价值）。详见笔记 `notes/2026-09-19-mcp-工具-annotations-挂起待搭车sdk-已支持判定标准采用-memos-覆盖既有状态说.md` |
| 2 | structuredContent + outputSchema（对象形规范化，修 #6022/#6139） | `call_tool` 返回 `list[TextContent]`，JSON 塞文本（server.py:114-119）；本仓作为客户端已在 cbm_client.py:314-315 消费外部 MCP 的 structuredContent，但自己不产出 | **deferred**：本仓工具返回值都是 JSON 对象（无裸数组/标量问题），当前宿主未见 strict 校验拒绝。若未来宿主普遍启用 outputSchema 校验再跟进；届时错误也应改走 `isError` 而非 200 文本里的 `{"error":...}`（registry.py:3249 现状） |
| 3 | 错误形状：`IsError: true` + 无 structuredContent | dispatch 把错误序列化成成功结果里的 JSON error 文本（registry.py:3249），宿主无法从协议层区分成败 | **deferred**（与 #2 同根）：改契约涉及全部 handler 与既有测试，等 #2 触发条件成立时一并做 |
| 4 | 任务级 eval（15 QA 钉种子数据，测工具组合可答性） | 有单测/集成测试测 handler 正确性，无"LLM 用工具完成任务"层面的评估 | **deferred**：与 llm-wiki-compiler 调研 #1/#9 同根（质量量化主线）。本仓若做，需先构造确定性种子仓库 + 固定问答集，成本高于 memos（其种子是现成 dump.sql）；待 lint 评分线立项后再评估 |
| 5 | OpenAPI 单一事实源驱动工具目录 | 本仓无 REST API 层，registry 手写 schema 本身就是单一事实源 | **excluded**：前提不成立（无 OpenAPI 可派生）；但"覆盖表引用必须存在、否则启动报错"的防静默失配习惯值得记住（对应本仓 registry 若加 per-tool 覆盖时应同样 fail-fast） |
| 6 | 进程内回环执行（工具=内部 HTTP 请求） | dispatch 直接动态 import handler 调用（registry.py:3251-3268），无 HTTP 中间层 | **excluded**：等价——本仓 handler 直调就是"复用同一逻辑面"，且少一层序列化开销 |
| 7 | CEL→SQL 编译器（结构化过滤语言） | 检索是 jieba 分词 + BM25 + 本体扩展的文本检索（cache.py:39-55），无结构化过滤需求 | **excluded**：本仓存储是 markdown 文件非 SQL，过滤语言无落点 |
| 8 | goldmark AST transformer（#tag 语法扩展） | wikilink 在 lint/render 层正则处理，无 AST 需求 | **excluded**：markdown 是存储格式不是渲染管线，AST 扩展无用武之地 |
| 9 | 静态目录 TTL（不广告 listChanged，打 24h ttlMs） | 本仓 stdio 传输，工具集同样进程内固定 | **excluded**：stdio 宿主不维持 discover 流，TTL 无意义；若未来加 HTTP 传输可回看 service.go:101-119 |
| 10 | Store Driver 接口（按聚合声明 CRUD + 三方言驱动） | 「统一知识存储层（KnowledgeStore 动词式门面）」任务进行中 | **exorcluded→参考**：不直接借鉴（memos 按聚合名词分接口，本仓门面是动词式），但其"接口即契约、方言差异封装在驱动实现"的分层可作为该任务的对照参考 |

## 4. 结论

memos 与本仓业务无关，但其 MCP server 是**协议合规工程**的教科书样本：annotations 从方法推导再逐操作修正、structuredContent 规范化修 strict 客户端、错误结果刻意不带 schema、覆盖表 fail-fast、任务级 eval 测工具可组合性——每一项都对应一个真实 issue（#6022/#6139），不是 speculative 设计。

对照处置：
- **一条 absorbed**：工具 annotations（#1），2026-09-19 grill 轮裁决为**挂起搭车**——SDK 已支持、判定标准已定（memos 覆盖既有状态说），等下次 registry 契约变更时顺路落地，不单独立项。
- **两条 deferred 同根主线**：structuredContent/错误形状（#2/#3，等 strict 宿主出现）、任务级 eval（#4，并入质量量化主线，与 llm-wiki-compiler 调研结论合流）。
- 其余 excluded：或前提不成立（无 OpenAPI/无 SQL 存储），或本仓已有等价实现。再次验证「借鉴调研先证伪」——36 个工具的 MCP server 真正值得搬的只有协议层的三个小机制。

## 附：基线

- 仓库：https://github.com/usememos/memos
- 基线：v0.31.0-rc.2-16-g7e3d3c6，HEAD 7e3d3c6（2026-09-19），下次增量调研以此为基线。
- 本地克隆：D:\repos\memos
