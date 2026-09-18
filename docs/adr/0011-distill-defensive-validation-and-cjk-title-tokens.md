# ADR-0011: 蒸馏 LLM 输出防御性校验与中文标题分词复用

- 状态：已接受
- 日期：2026-09-18
- 关联任务：产品维护（源自「他山之石」graphiti 调研，报告见 `docs/graphiti-调研与借鉴分析.md`）

## 背景

graphiti 调研（getzep/graphiti，HEAD de8eb5b）提炼出「LLM 输出防御性校验」与「确定性快路径 + LLM 兜底」两个工程习惯。对照 CodeWiki 代码核对后发现两处真实缺口，且严重度高于调研报告初判：

### 缺口 C：解析失败静默销毁原料

`_parse_llm_notes`（distill_conversation.py:907-932）对烂 JSON best-effort 解析，失败返回 `[]`。下游 `_process_llv_output` 据此判 `no_knowledge`，随后 raw 文件被当噪声**永久删除**（distill_conversation.py:1259-1265）。LLM 输出格式烂掉 = 原始对话数据丢失，且调用方无法区分「确实无知识」与「解析失败」——违反 Doctrine「不静默失败」与「候选必有去向」。

### 缺口 E：中文标题进不了标题 Jaccard 冲突带

`_title_tokens`（distill_conversation.py:460-462）按空白/下划线/连字符切分，中文标题无空格，整题成单 token。「发版本」vs「发版本流程」Jaccard = 0.0，纯中文标题对**永远进不了** [0.35, 0.6) 弱冲突带，中文冲突检测实际只靠 BM25 兜底。而 `retrieval.py:215-238` 已有 jieba 分词器（`tokenize`，含停用词过滤），却未被复用——违反「单点收敛」。

## 决策

1. **C 修复——解析失败不再销毁原料**：`_parse_llm_notes` 改为返回 `(notes, parse_error)` 二元组；`_process_llm_output` 在 `parse_error` 非空时跳过 `_mark_distilled` 与删除/归档逻辑，raw 保留在 raw/ 等待重试，响应新增 `parse_error` 字段显式报告。Mode A/B 的 `_distill_one` 同步透传。
2. **E 修复——分词单点收敛**：`_title_tokens` 复用 `codewiki.src.retrieval.tokenize`（jieba 优先、regex 兜底、停用词过滤）。中文标题获得真实 token 集，Jaccard 弱冲突带对中文生效；英文行为不变（tokenize 同样按词切分）。不引入新阈值、不加熵门控。
3. **单条 note 字段校验**：`_process_llm_output` 循环内对缺 `title`/`content` 的条目剔除并记入 `produced`（status=`invalid_note`），不静默丢弃。
4. **测试**：`tests/test_distill_defensive.py` 新增——烂 JSON 保留 raw、中文标题 Jaccard 生效、缺字段 note 剔除；既有 smoke 测试断言 `bad == []` 改为断言二元组形状。

### Round 2 增补（grill 第二轮，实测驱动）

5. **子集标题降级**：E 修复后实测发现「任务记忆压缩」vs「任务记忆压缩设计方案」= 0.75 直落强重复带自动 suppress，属误杀。新增 `_is_title_subset`：token 集真子集且 sim ∈ [0.6, 0.8) 的标题对降级到弱冲突带交 agent 裁决；≥0.8 的近全同改写（如只差一个填充词）与完全相同标题仍走快路径。接入 `_find_existing_note` 与 `_find_conflict_candidates` 两处强判定。
6. **parse_error 落 frontmatter**：`_mark_parse_failed` 在 raw frontmatter 写入 `parse_error: <原因>`（status 保持 pending），下轮 worker 重读时第一眼可见失败原因，无需重读全文。
7. **测试增补**：子集检测（含 0.857 近全同不降级）、子集标题不自动 suppress、相同标题仍快路径、parse_error 落 frontmatter。

## 后果

- **正面**：解析失败可重试（原料不丢）；中文近重复标题进入 agent 裁决带（此前只有 BM25 能捞到）；LLM 输出形状错误不再静默。
- **负面**：`_parse_llm_notes` 签名变更，Mode A/B 调用点需同步改；jieba 未安装时退回 regex 切分，中文冲突带仍部分失效（与现状一致，不劣化）。
- **不做**：检索 recipe 预设化（等调用方抱怨参数面再做）；退役时间维度（ADR-0009 刚落地，先观察）。

## 依据

- graphiti 防御性校验：node_operations.py:560-601（越界 ID 剔除+告警）
- graphiti 分层去重：node_operations.py:627、dedup_helpers.py:236-277
- CodeWiki 现状核对：distill_conversation.py:907-932、:460-462、:1259-1265、retrieval.py:215-238
