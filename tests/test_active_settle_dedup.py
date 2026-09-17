"""ADR-0008 原料标记去重：capture_conversation 的 ``active_settle`` 顶层单行键
+ distill_conversation 见标记只产草稿笔记、跳过任务记忆（显式声明，不静默）。

覆盖工单 02 的四类断言：
a. 带 ``active_settle=true`` 的采集，落盘 frontmatter 含顶层单行 ``active_settle: true``
   （stdlib-only hook 逐行扫描可命中——模拟扫描断言）；
b. 该 raw 蒸馏后：产出草稿笔记、不写任务记忆；响应含 ``memories_skipped_reason``；
c. 不带标记的蒸馏行为不变（记忆照写，响应无跳过字段）；
d. 同会话 supersede 重采后标记随新值生效（就地覆盖路径）。
"""

import json

from codewiki.mcp.session import SessionStore
from codewiki.mcp.tools import capture_conversation as capture
from codewiki.mcp.tools import distill_conversation as distill
from codewiki.mcp.tools import task_manager as tm


# --------------------------------------------------------------------------- #
# Helpers（对齐 test_task_manager.py 的调用风格）
# --------------------------------------------------------------------------- #


def _store() -> SessionStore:
    return SessionStore()


def _call(fn, **kwargs) -> dict:
    return json.loads(fn(kwargs, _store()))


def _raw_file(repo: str, conversation_id: str):
    from pathlib import Path

    return Path(repo) / "repowiki" / "raw" / f"{conversation_id}.md"


def _scan_top_level_lines(text: str, key: str) -> list:
    """模拟 stdlib-only hook 的逐行扫描：命中形如 ``key: value`` 的行。"""
    return [ln for ln in text.splitlines() if ln.startswith(f"{key}:")]


def _frontmatter_block(text: str) -> str:
    """首个 ``---`` 块（不含闭合线）。"""
    assert text.startswith("---")
    end = text.find("\n---", 3)
    assert end != -1
    return text[3:end]


# --------------------------------------------------------------------------- #
# a. 采集：active_settle 透传为 frontmatter 顶层单行键
# --------------------------------------------------------------------------- #


def test_capture_active_settle_lands_as_top_level_single_line(tmp_path):
    repo = str(tmp_path)
    cap = _call(
        capture.handle_capture_conversation,
        repo_path=repo,
        conversation=[
            {"role": "user", "content": "带标记的采集会话"},
            {"role": "assistant", "content": "本会话记忆已主动沉淀"},
        ],
        active_settle=True,
    )
    assert cap["status"] == "captured"

    text = _raw_file(repo, cap["conversation_id"]).read_text(encoding="utf-8")
    # 逐行扫描（模拟 .codebuddy/.trae hook 的读法）命中唯一一行
    assert _scan_top_level_lines(text, "active_settle") == ["active_settle: true"]
    # 且位于 frontmatter 块内（顶层、单行，非嵌套缩进）
    assert "active_settle: true" in _frontmatter_block(text).splitlines()


def test_capture_without_marker_writes_no_active_settle_key(tmp_path):
    repo = str(tmp_path)
    cap = _call(
        capture.handle_capture_conversation,
        repo_path=repo,
        conversation=[
            {"role": "user", "content": "无标记的采集会话"},
            {"role": "assistant", "content": "常规批处理路径"},
        ],
    )
    assert cap["status"] == "captured"
    text = _raw_file(repo, cap["conversation_id"]).read_text(encoding="utf-8")
    # 无标记时 frontmatter 不新增任何键（逐字节不变约束）
    assert _scan_top_level_lines(text, "active_settle") == []


# --------------------------------------------------------------------------- #
# b. 蒸馏：见标记只产草稿笔记、跳过任务记忆，响应显式声明
# --------------------------------------------------------------------------- #


def test_distill_active_settle_produces_notes_skips_memories(tmp_path):
    repo = str(tmp_path)
    r = _call(tm.handle_create_task, repo_path=repo, title="去重任务")
    task_id = r["task"]["id"]

    cap = _call(
        capture.handle_capture_conversation,
        repo_path=repo,
        conversation=[
            {"role": "user", "content": "帮我确认部署流程"},
            {"role": "assistant", "content": "已完成部署，采用蓝绿方案"},
        ],
        task_id=task_id,
        active_settle=True,
    )
    cid = cap["conversation_id"]

    sub = _call(
        distill.handle_distill_conversation,
        repo_path=repo,
        mode="submit",
        distilled={
            cid: {
                "notes": [
                    {
                        "title": "部署采用蓝绿方案",
                        "note_type": "decision",
                        "content": "## 背景\n\n选型\n\n## 决策\n\n蓝绿部署",
                    }
                ],
                "memories": ["本会话完成蓝绿部署"],
            },
        },
    )
    assert sub["status"] == "completed"
    per = sub["distilled"][0]
    # 笔记路径不受影响：草稿照产
    assert per["notes_created"] == 1
    # 任务记忆被跳过：不写入
    assert per["memories_written"] == 0
    # 跳过不静默：响应显式声明原因
    assert per["memories_skipped_reason"] == "active_settle"

    # 落盘事实：任务记忆为空，草稿笔记存在
    got = _call(tm.handle_get_task, repo_path=repo, task_id=task_id)
    assert got["memories_total"] == 0


# --------------------------------------------------------------------------- #
# c. 无标记行为不变：记忆照写，响应无跳过字段
# --------------------------------------------------------------------------- #


def test_distill_without_marker_writes_memories_unchanged(tmp_path):
    repo = str(tmp_path)
    r = _call(tm.handle_create_task, repo_path=repo, title="常规任务")
    task_id = r["task"]["id"]

    cap = _call(
        capture.handle_capture_conversation,
        repo_path=repo,
        conversation=[
            {"role": "user", "content": "帮我实现常规任务的导出功能"},
            {"role": "assistant", "content": "已实现导出，采用 CSV 方案"},
        ],
        task_id=task_id,
    )
    cid = cap["conversation_id"]

    sub = _call(
        distill.handle_distill_conversation,
        repo_path=repo,
        mode="submit",
        distilled={
            cid: {
                "notes": [
                    {
                        "title": "导出采用 CSV 方案",
                        "note_type": "decision",
                        "content": "## 背景\n\n选型\n\n## 决策\n\nCSV",
                    }
                ],
                "memories": ["本会话完成 CSV 导出"],
            },
        },
    )
    assert sub["status"] == "completed"
    per = sub["distilled"][0]
    assert per["notes_created"] == 1
    assert per["memories_written"] == 1
    # 无标记：响应不携带跳过声明
    assert "memories_skipped_reason" not in per

    got = _call(tm.handle_get_task, repo_path=repo, task_id=task_id)
    assert "CSV 导出" in got["memories"]


# --------------------------------------------------------------------------- #
# d. 同会话 supersede 重采：标记随新值生效（就地覆盖路径）
# --------------------------------------------------------------------------- #


def test_supersede_recapture_updates_marker(tmp_path):
    repo = str(tmp_path)
    r = _call(tm.handle_create_task, repo_path=repo, title="重采任务")
    task_id = r["task"]["id"]
    sid = "ide-session-settle"

    # 首次采集：不带标记
    cap1 = _call(
        capture.handle_capture_conversation,
        repo_path=repo,
        conversation=[
            {"role": "user", "content": "第一次采集的内容"},
            {"role": "assistant", "content": "第一次回答"},
        ],
        source_session_id=sid,
        task_id=task_id,
    )
    assert cap1["status"] == "captured"
    assert _scan_top_level_lines(
        _raw_file(repo, cap1["conversation_id"]).read_text(encoding="utf-8"),
        "active_settle",
    ) == []

    # 同会话重采（收尾轮保险采集，带标记）：就地覆盖，仍是单文件
    cap2 = _call(
        capture.handle_capture_conversation,
        repo_path=repo,
        conversation=[
            {"role": "user", "content": "第一次采集的内容"},
            {"role": "assistant", "content": "第一次回答"},
            {"role": "user", "content": "收尾补充"},
            {"role": "assistant", "content": "收尾回答，记忆已沉淀"},
        ],
        source_session_id=sid,
        task_id=task_id,
        active_settle=True,
    )
    assert cap2["status"] == "captured"
    assert cap2["superseded"] is True
    assert cap2["conversation_id"] == cap1["conversation_id"]

    text = _raw_file(repo, cap2["conversation_id"]).read_text(encoding="utf-8")
    assert _scan_top_level_lines(text, "active_settle") == ["active_settle: true"]
    # 覆盖后正文是新转录
    assert "收尾补充" in text

    # 覆盖后的 raw 蒸馏：标记生效，跳过记忆、笔记照产
    sub = _call(
        distill.handle_distill_conversation,
        repo_path=repo,
        mode="submit",
        distilled={
            cap2["conversation_id"]: {
                "notes": [
                    {
                        "title": "重采会话的经验",
                        "note_type": "general",
                        "content": "## 背景\n\nx\n\n## 结论\n\ny",
                    }
                ],
                "memories": ["不应写入的记忆"],
            },
        },
    )
    per = sub["distilled"][0]
    assert per["notes_created"] == 1
    assert per["memories_written"] == 0
    assert per["memories_skipped_reason"] == "active_settle"

    got = _call(tm.handle_get_task, repo_path=repo, task_id=task_id)
    assert got["memories_total"] == 0


# --------------------------------------------------------------------------- #
# MCP schema：capture_conversation 声明可选布尔参数
# --------------------------------------------------------------------------- #


def test_registry_schema_declares_active_settle():
    from codewiki.mcp.registry import REGISTRY

    props = REGISTRY["capture_conversation"].schema.inputSchema["properties"]
    assert "active_settle" in props
    assert props["active_settle"]["type"] == "boolean"
    assert "active_settle" not in REGISTRY["capture_conversation"].schema.inputSchema.get(
        "required", []
    )
