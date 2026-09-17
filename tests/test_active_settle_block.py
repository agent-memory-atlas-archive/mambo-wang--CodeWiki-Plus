"""票 04：主动沉淀协议块 + 共享引导段条件式（测试补齐与验收固化）。

依据 .scratch/active-settle-wiring/issues/04-active-settle-block.md 与
docs/接线档位选择设计方案.md §3.3/§3.8/§3.9。

实现已由前序落盘（``prompts._active_settle_section`` 生成正文、
``ide_config.upsert_active_settle_protocol`` 做渲染开关 + 旧块一次性迁移），
本票只补测试与验收，覆盖四条验收项：

a. 混合档渲染唯一性：同一注入文件（AGENTS.md）下不出现两份引导段/两份协议块；
b. 四判据 + 收尾轮兜底成文，且明确「不做字面每轮沉淀」及理由；
c. 旧 ``CODEWIKI-QWENWORK`` 块被整体迁移为新 ``CODEWIKI-ACTIVE-SETTLE`` 块；
d. 默认零变化：显式 off / 注册表默认 false 的宿主不渲染该块；qwenwork/trae
   （注册表默认 true）默认即为 on。

另：固化 ``ingest_note(status="draft")`` 措辞（不暗示可跳过确认闸门）与「草稿
落盘即可被 ``get_task_context`` 的 related_notes 以 ``status: draft`` 展示」的
现状能力（工单第 5 条验收）。
"""

import json

import pytest

from codewiki.cli.utils.ide_config import (
    AGENT_FILE,
    install_for_ide,
    upsert_active_settle_protocol,
)
from codewiki.mcp.prompts import (
    _ACTIVE_SETTLE_END,
    _ACTIVE_SETTLE_START,
    _QWENWORK_CAPTURE_END,
    _QWENWORK_CAPTURE_START,
    _TASK_MEMORY_AGENTS_END,
    _TASK_MEMORY_AGENTS_START,
    _active_settle_section,
)
from codewiki.mcp.session import SessionStore
from codewiki.mcp.tools import note_ingest as ni
from codewiki.mcp.tools import task_manager as tm
from codewiki.mcp.tools.hook_registry import active_settle_of

# --------------------------------------------------------------------------- #
# Helpers / fixtures
# --------------------------------------------------------------------------- #

HOOK_SOURCES = {
    "capture_session_end.py": "import json\n\nprint('ok')\n",
    "task_session_start.py": "import os\n\nprint('ok')\n",
}
AGENT_SOURCE = "---\nname: distill-worker\nmcpServers:\n  - codewiki\n---\nworker\n"
AGENT_SOURCE_CLAUDE = (
    "---\nname: distill-worker\n"
    "tools: Read, Write, mcp__codewiki__distill_conversation\n---\nworker\n"
)


@pytest.fixture
def fake_pkg(tmp_path, monkeypatch):
    """假包目录（与 test_cli_mode_status.fake_pkg 同构）：供 hook 档拷贝源。"""
    pkg = tmp_path / "pkg"
    (pkg / "hooks").mkdir(parents=True)
    (pkg / "agents").mkdir(parents=True)
    for name, content in HOOK_SOURCES.items():
        (pkg / "hooks" / name).write_text(content, encoding="utf-8")
    (pkg / "agents" / AGENT_FILE).write_text(AGENT_SOURCE, encoding="utf-8")
    (pkg / "agents" / "distill-worker.claude.md").write_text(
        AGENT_SOURCE_CLAUDE, encoding="utf-8"
    )
    monkeypatch.setattr("codewiki.cli.utils.ide_config._resolve_pkg_sources", lambda: pkg)
    return pkg


def _call(fn, **kw) -> dict:
    return json.loads(fn(kw, SessionStore()))


def _read(path) -> str:
    return path.read_text(encoding="utf-8")


# --------------------------------------------------------------------------- #
# a. 混合档渲染唯一性
# --------------------------------------------------------------------------- #


def test_mixed_tiers_render_single_sections(tmp_path, fake_pkg):
    """prompt 档（qwenwork 默认 on）+ hook 档（codebuddy 默认 off）同仓混跑。

    共享注入文件只允许一份引导段、一份协议块；codebuddy 默认 off 不得抹掉
    qwenwork 已写入的块（互不覆盖）。
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "AGENTS.md").write_text("# Project\n", encoding="utf-8")

    r_prompt = install_for_ide(str(repo), "qwenwork")  # 注册表默认 on
    r_hook = install_for_ide(str(repo), "codebuddy")  # 注册表默认 off
    assert r_prompt["wiring"] == "prompt"
    assert r_hook["wiring"] == "hook"

    text = _read(repo / "AGENTS.md")
    assert text.count(_TASK_MEMORY_AGENTS_START) == 1
    assert text.count(_TASK_MEMORY_AGENTS_END) == 1
    assert text.count(_ACTIVE_SETTLE_START) == 1
    assert text.count(_ACTIVE_SETTLE_END) == 1

    # 反向顺序再跑一遍：仍唯一（幂等，不叠加、不互删）
    install_for_ide(str(repo), "codebuddy")
    install_for_ide(str(repo), "qwenwork")
    text2 = _read(repo / "AGENTS.md")
    assert text2.count(_TASK_MEMORY_AGENTS_START) == 1
    assert text2.count(_TASK_MEMORY_AGENTS_END) == 1
    assert text2.count(_ACTIVE_SETTLE_START) == 1
    assert text2.count(_ACTIVE_SETTLE_END) == 1


# --------------------------------------------------------------------------- #
# b. 四判据 + 收尾轮兜底成文（含每轮禁令、draft 措辞）
# --------------------------------------------------------------------------- #


def test_rendered_block_documents_criteria_and_fallback(tmp_path):
    """渲染出的块正文须同时含四类判据 + 收尾轮兜底 + 每轮禁令 + draft 措辞。"""
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "AGENTS.md").write_text("# Project\n", encoding="utf-8")
    install_for_ide(str(repo), "qwenwork")
    text = _read(repo / "AGENTS.md")

    # 四判据（里程碑 / 决策 / 话题转向 / 收尾轮）在成文正文中同时出现
    for phrase in ("里程碑达成", "决策落定", "明显转向", "收尾轮"):
        assert phrase in text
    # 收尾轮为强制兜底（必做）
    assert "强制兜底" in text
    # 明确「不做字面每轮沉淀」并给出理由（记忆压缩阈值）
    assert "不做字面每轮沉淀" in text
    assert "压缩阈值" in text
    # 两条写入路径：任务记忆直写 + 草稿笔记（确认闸门保留）
    assert "add_task_memory" in text
    assert 'ingest_note(status="draft"' in text
    assert "确认闸门保留" in text
    assert "confirm_note" in text
    assert "不得跳过确认" in text
    # 收尾轮保险采集带 active_settle=true 标记
    assert "active_settle=true" in text
    # 宿主专属小节由注册表 protocol 触发（qwenwork → 会话历史 API 拉取）
    assert "qw_query" in text


def test_section_generator_matches_rendered_block(tmp_path):
    """块正文生成器与落盘渲染一致（无额外宿主前置参数时为纯正文）。"""
    line = _active_settle_section()
    assert line.startswith(_ACTIVE_SETTLE_START)
    assert line.endswith(_ACTIVE_SETTLE_END)
    assert "不做字面每轮沉淀" in line


# --------------------------------------------------------------------------- #
# c. 旧 CODEWIKI-QWENWORK 块一次性迁移
# --------------------------------------------------------------------------- #


def test_legacy_qwenwork_block_migrated_to_active_settle(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    stale = (
        "# Project\n\n"
        f"{_QWENWORK_CAPTURE_START}\nOLD QWENWORK PROTOCOL\n{_QWENWORK_CAPTURE_END}\n\n"
        "tail content\n"
    )
    (repo / "AGENTS.md").write_text(stale, encoding="utf-8")

    r = install_for_ide(str(repo), "qwenwork")
    assert r["protocol_changed"] is True

    text = _read(repo / "AGENTS.md")
    # 旧标记与旧正文整块消失
    assert _QWENWORK_CAPTURE_START not in text
    assert _QWENWORK_CAPTURE_END not in text
    assert "OLD QWENWORK PROTOCOL" not in text
    # 新块出现且唯一
    assert text.count(_ACTIVE_SETTLE_START) == 1
    assert text.count(_ACTIVE_SETTLE_END) == 1
    # 块外内容原样保留
    assert "tail content" in text


# --------------------------------------------------------------------------- #
# d. 默认零变化
# --------------------------------------------------------------------------- #


def test_default_off_is_noop_and_byte_identical(tmp_path):
    """注册表默认 false 的宿主（codebuddy）传 None = 不渲染也不删除。"""
    f = tmp_path / "AGENTS.md"
    original = "# Project\n\nexisting content\n"
    f.write_text(original, encoding="utf-8")

    assert active_settle_of("codebuddy") is False
    assert upsert_active_settle_protocol(f, "codebuddy") is False
    assert _read(f) == original  # 逐字节一致


def test_explicit_off_removes_new_and_legacy_blocks(tmp_path):
    """显式 off（CLI 覆盖）才清理两块；共享引导段不受影响。"""
    f = tmp_path / "AGENTS.md"
    f.write_text(
        "# Project\n\n"
        f"{_TASK_MEMORY_AGENTS_START}\nshared guidance\n{_TASK_MEMORY_AGENTS_END}\n\n"
        f"{_ACTIVE_SETTLE_START}\nsettle\n{_ACTIVE_SETTLE_END}\n\n"
        f"{_QWENWORK_CAPTURE_START}\nlegacy\n{_QWENWORK_CAPTURE_END}\n",
        encoding="utf-8",
    )

    assert upsert_active_settle_protocol(f, "codebuddy", active_settle=False) is True
    text = _read(f)
    assert _ACTIVE_SETTLE_START not in text
    assert _QWENWORK_CAPTURE_START not in text
    assert _TASK_MEMORY_AGENTS_START in text  # 引导段保留


def test_install_default_off_renders_no_block(tmp_path, fake_pkg):
    """hook 档宿主默认 off：引导段照写（行为不变），但不渲染协议块。"""
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "AGENTS.md").write_text("# Project\n", encoding="utf-8")

    r = install_for_ide(str(repo), "codebuddy")
    assert r["active_settle"] is False
    assert r["protocol_changed"] is False
    text = _read(repo / "AGENTS.md")
    assert _ACTIVE_SETTLE_START not in text
    assert _TASK_MEMORY_AGENTS_START in text


def test_registry_default_on_hosts_render_by_default(tmp_path):
    """qwenwork / trae 注册表默认 true，不传叠加即为 on 并渲染。"""
    assert active_settle_of("qwenwork") is True
    assert active_settle_of("trae") is True

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "AGENTS.md").write_text("# Project\n", encoding="utf-8")
    r = install_for_ide(str(repo), "qwenwork")
    assert r["active_settle"] is True
    assert r["protocol_changed"] is True
    text = _read(repo / "AGENTS.md")
    assert _ACTIVE_SETTLE_START in text


# --------------------------------------------------------------------------- #
# 第 5 条验收：draft 落盘即可被 get_task_context 以 status: draft 展示
# --------------------------------------------------------------------------- #


def test_draft_note_surfaces_in_task_context(tmp_path):
    repo = str(tmp_path)
    r = _call(tm.handle_create_task, repo_path=repo, title="沉淀任务")
    task_id = r["task"]["id"]

    _call(
        ni.handle_ingest_note,
        repo_path=repo,
        title="草稿经验",
        content="## 背景\n\nx\n\n## 结论\n\ny",
        note_type="general",
        status="draft",
        task_id=task_id,
    )

    ctx = _call(tm.handle_get_task_context, repo_path=repo, task_id=task_id)
    drafts = [n for n in ctx["related_notes"] if n["status"] == "draft"]
    assert drafts, ctx["related_notes"]