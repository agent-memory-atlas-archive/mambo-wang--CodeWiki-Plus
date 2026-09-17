"""票 05：换档 / 换叠加清理——幂等可逆，只删自己的条目。

依据 docs/接线档位选择设计方案.md §3.10 与
.scratch/active-settle-wiring/issues/05-switch-cleanup.md：

  - hook → prompt：移除我们的 hook 注册条目（command 命中相对脚本后缀的才删，
    复用 ``_relative_hook_suffix``，兼容正/反斜杠历史条目）；他人条目与
    settings 其他键原样保留；默认保留 .py 脚本与 distill-worker.md，
    ``--clean`` 才删脚本与 distill-worker.md。
  - active_settle on → off：删注入文件里的 CODEWIKI-ACTIVE-SETTLE 块；共享引导块
    的收尾步本就是条件式，块消失后自动回落到「传统收尾轮采集」。
  - 往返等价 + 两次 install 幂等（产物逐字节不变）。
"""

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from codewiki.cli.commands.install_hooks import install_hooks
from codewiki.cli.utils.ide_config import (
    AGENT_FILE,
    HOOK_FILES,
    install_for_ide,
    unwire_hook_registration,
)
from codewiki.mcp.prompts import (
    _ACTIVE_SETTLE_END,
    _ACTIVE_SETTLE_START,
    _QWENWORK_CAPTURE_START,
    _TASK_MEMORY_AGENTS_END,
    _TASK_MEMORY_AGENTS_START,
)

HOOK_SOURCES = {
    "capture_session_end.py": "import json\n\nprint('ok')\n",
    "task_session_start.py": "import os\n\nprint('ok')\n",
}
AGENT_SOURCE = "---\nname: distill-worker\nmcpServers:\n  - codewiki\n---\nworker\n"
AGENT_SOURCE_CLAUDE = (
    "---\nname: distill-worker\n"
    "tools: Read, Write, mcp__codewiki__distill_conversation\n---\nworker\n"
)

# 他人（非 CodeWiki）hook 条目：往返全程必须零改动。
FOREIGN_END_ENTRY = {
    "matcher": "other",
    "hooks": [{"type": "command", "command": "my-other-tool --on-exit", "timeout": 5}],
}
FOREIGN_UP_ENTRY = {
    "matcher": "startup",
    "hooks": [{"type": "command", "command": "my-own-hook", "timeout": 5}],
}


@pytest.fixture
def fake_pkg(tmp_path, monkeypatch):
    """假包目录（与 test_install_hooks.fake_pkg 同构）：提供接线源副本。"""
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


def _snapshot(root: Path) -> dict[str, bytes]:
    """递归快照目录内容（相对路径 → 字节），用于幂等逐字节比对。"""
    return {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _all_commands(data: dict) -> list[str]:
    out: list[str] = []
    for entries in (data.get("hooks") or {}).values():
        for entry in entries:
            for h in entry.get("hooks") or []:
                if isinstance(h, dict) and isinstance(h.get("command"), str):
                    out.append(h["command"])
    return out


def _extract(text: str, start: str, end: str) -> str:
    i = text.find(start)
    j = text.find(end)
    return text[i : j + len(end)]


# ---------------------------------------------------------------------------
# 换档：hook → prompt → hook 往返等价 + 他人条目零改动
# ---------------------------------------------------------------------------


def test_hook_prompt_hook_roundtrip_settings_equivalent(tmp_path, fake_pkg):
    (tmp_path / ".codebuddy").mkdir()
    settings_path = tmp_path / ".codebuddy" / "settings.json"
    settings_path.write_text(
        json.dumps(
            {"telemetry": {"enabled": True}, "hooks": {"SessionEnd": [FOREIGN_END_ENTRY]}},
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    install_for_ide(str(tmp_path), "codebuddy", mode="hook")
    wired = _read_json(settings_path)
    # 首次 hook 档：我们的 3 类命令都在，他人条目仍在。
    assert any("task_session_start.py" in c for c in _all_commands(wired))

    # 换档 prompt：只摘除我们的条目。
    install_for_ide(str(tmp_path), "codebuddy", mode="prompt")
    unwired = _read_json(settings_path)
    # settings 其他键原样保留。
    assert unwired["telemetry"] == {"enabled": True}
    # 他人条目零改动（强断言：整条 dict 相等）。
    assert unwired["hooks"]["SessionEnd"] == [FOREIGN_END_ENTRY]
    # 我们的条目全部消失（脚本后缀 + 常量 python -m 入口）。
    commands = _all_commands(unwired)
    assert not any("task_session_start.py" in c for c in commands)
    assert not any("capture_session_end.py" in c for c in commands)
    assert not any("_ide_hook" in c for c in commands)

    # 换回 hook：与首次 hook 后等价（往返闭合）。
    install_for_ide(str(tmp_path), "codebuddy", mode="hook")
    rewired = _read_json(settings_path)
    assert rewired == wired
    # 他人条目依旧原样，我们的 end 命令重新挂回同一 matcher 条目内。
    assert FOREIGN_END_ENTRY["hooks"][0] in rewired["hooks"]["SessionEnd"][0]["hooks"]


def test_unwire_keeps_foreign_user_prompt_submit(tmp_path, fake_pkg):
    (tmp_path / ".codebuddy").mkdir()
    settings_path = tmp_path / ".codebuddy" / "settings.json"
    settings_path.write_text(
        json.dumps({"hooks": {"UserPromptSubmit": [FOREIGN_UP_ENTRY]}}, ensure_ascii=False),
        encoding="utf-8",
    )

    install_for_ide(str(tmp_path), "codebuddy", mode="hook")
    install_for_ide(str(tmp_path), "codebuddy", mode="prompt")

    data = _read_json(settings_path)
    # 他人的 UserPromptSubmit 规则原样保留，只有我们的常量命令被摘除。
    assert data["hooks"]["UserPromptSubmit"] == [FOREIGN_UP_ENTRY]


@pytest.mark.parametrize(
    "legacy_start",
    [
        'python "D:/repos/proj/.qoder/hooks/task_session_start.py"',
        'python "D:\\repos\\proj\\.qoder\\hooks\\task_session_start.py"',
        'python "$CLAUDE_PROJECT_DIR/.qoder/hooks/task_session_start.py"',
    ],
)
def test_unwire_matches_legacy_entries_and_is_idempotent(tmp_path, legacy_start):
    (tmp_path / ".qoder").mkdir()
    settings_path = tmp_path / ".qoder" / "settings.json"
    settings_path.write_text(
        json.dumps(
            {
                "hooks": {
                    "SessionStart": [
                        {
                            "matcher": "startup",
                            "hooks": [
                                {"type": "command", "command": legacy_start, "timeout": 15}
                            ],
                        }
                    ]
                }
            }
        ),
        encoding="utf-8",
    )

    assert unwire_hook_registration(str(tmp_path), "qoder") is True
    data = _read_json(settings_path)
    # 该 event 原本只有我们的历史条目 → 条目删空后 hooks 键一并还原。
    assert "hooks" not in data
    # 幂等：第二次无我们的条目 → 无操作、不产生写入。
    assert unwire_hook_registration(str(tmp_path), "qoder") is False


def test_unwire_never_clears_hooks_key_when_foreign_remain(tmp_path):
    # 铁律：绝不整段清空 hooks 键；只摘除我们的条目。
    (tmp_path / ".qoder").mkdir()
    settings_path = tmp_path / ".qoder" / "settings.json"
    settings_path.write_text(
        json.dumps(
            {
                "hooks": {
                    "SessionEnd": [FOREIGN_END_ENTRY],
                    "SessionStart": [
                        {
                            "matcher": "startup",
                            "hooks": [
                                {
                                    "type": "command",
                                    "command": 'python ".qoder/hooks/task_session_start.py"',
                                    "timeout": 15,
                                }
                            ],
                        }
                    ],
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    assert unwire_hook_registration(str(tmp_path), "qoder") is True
    data = _read_json(settings_path)
    assert data["hooks"]["SessionEnd"] == [FOREIGN_END_ENTRY]
    assert "SessionStart" not in data["hooks"]  # 只有我们的 event 被移除


# ---------------------------------------------------------------------------
# 换叠加：active_settle on → off → on 往返等价
# ---------------------------------------------------------------------------


def test_active_settle_on_off_on_roundtrip_agents_md(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    agents = repo / "AGENTS.md"
    agents.write_text("# Project\n\nexisting content\n", encoding="utf-8")

    # on：渲染新块（泛化取代旧 CODEWIKI-QWENWORK 块）。
    install_for_ide(str(repo), "qwenwork", active_settle=True)
    on_text = agents.read_text(encoding="utf-8")
    assert _ACTIVE_SETTLE_START in on_text and _ACTIVE_SETTLE_END in on_text
    assert _QWENWORK_CAPTURE_START not in on_text
    shared_on = _extract(on_text, _TASK_MEMORY_AGENTS_START, _TASK_MEMORY_AGENTS_END)

    # off：只删标记块，块外内容不动。
    install_for_ide(str(repo), "qwenwork", active_settle=False)
    off_text = agents.read_text(encoding="utf-8")
    assert _ACTIVE_SETTLE_START not in off_text and _ACTIVE_SETTLE_END not in off_text
    assert "existing content" in off_text
    # 共享引导块零改动——其收尾步本就是条件式（无 ACTIVE-SETTLE 块即走传统采集）。
    assert _extract(off_text, _TASK_MEMORY_AGENTS_START, _TASK_MEMORY_AGENTS_END) == shared_on
    assert "传统收尾轮采集" in off_text

    # on again：与初始 on 逐字节等价（往返闭合）。
    install_for_ide(str(repo), "qwenwork", active_settle=True)
    assert agents.read_text(encoding="utf-8") == on_text


def test_active_settle_off_removes_block_on_hook_host(tmp_path, fake_pkg):
    # 叠加与档位正交：hook 档宿主显式 on 也渲染块，显式 off 同样删除。
    (tmp_path / ".codebuddy").mkdir()
    install_for_ide(str(tmp_path), "codebuddy", mode="hook", active_settle=True)
    assert _ACTIVE_SETTLE_START in (tmp_path / "AGENTS.md").read_text(encoding="utf-8")

    install_for_ide(str(tmp_path), "codebuddy", mode="hook", active_settle=False)
    text = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert _ACTIVE_SETTLE_START not in text
    assert _TASK_MEMORY_AGENTS_START in text  # 共享引导块保留


# ---------------------------------------------------------------------------
# 幂等：任意档位/叠加连跑两次 = 跑一次（产物 diff 为空）
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "mode,active_settle",
    [("hook", None), ("prompt", None), ("prompt", True)],
)
def test_install_twice_is_byte_identical(tmp_path, fake_pkg, mode, active_settle):
    repo = tmp_path / "repo"
    (repo / ".qoder").mkdir(parents=True)
    kwargs = {"mode": mode}
    if active_settle is not None:
        kwargs["active_settle"] = active_settle

    install_for_ide(str(repo), "qoder", **kwargs)
    first = _snapshot(repo)
    install_for_ide(str(repo), "qoder", **kwargs)
    second = _snapshot(repo)
    assert second == first  # 产物逐字节不变


def test_prompt_clean_twice_is_idempotent(tmp_path, fake_pkg):
    (tmp_path / ".qoder").mkdir()
    install_for_ide(str(tmp_path), "qoder", mode="hook")  # 先铺好产物
    install_for_ide(str(tmp_path), "qoder", mode="prompt", clean=True)
    first = _snapshot(tmp_path)
    install_for_ide(str(tmp_path), "qoder", mode="prompt", clean=True)
    assert _snapshot(tmp_path) == first


# ---------------------------------------------------------------------------
# --clean：才删脚本与 distill-worker.md；不带时保留可复用
# ---------------------------------------------------------------------------


def test_clean_deletes_our_artifacts_only(tmp_path, fake_pkg):
    (tmp_path / ".qoder").mkdir()
    install_for_ide(str(tmp_path), "qoder", mode="hook")
    hooks_dir = tmp_path / ".qoder" / "hooks"
    agents_dir = tmp_path / ".qoder" / "agents"
    # 植入他人产物文件：任何情况下都不许被删。
    (hooks_dir / "other_tool.py").write_text("x = 1\n", encoding="utf-8")
    (agents_dir / "other-worker.md").write_text("other\n", encoding="utf-8")
    for name in HOOK_FILES:
        assert (hooks_dir / name).is_file()

    # 不带 --clean：注册条目移除，但脚本与 worker 保留可复用。
    kept = install_for_ide(str(tmp_path), "qoder", mode="prompt", clean=False)
    assert kept["cleaned"] == []
    for name in HOOK_FILES:
        assert (hooks_dir / name).is_file()
    assert (agents_dir / AGENT_FILE).is_file()

    # 带 --clean：删我们的产物，他人文件与目录本身保留。
    cleaned = install_for_ide(str(tmp_path), "qoder", mode="prompt", clean=True)
    assert {Path(p).as_posix() for p in cleaned["cleaned"]} == {
        ".qoder/hooks/capture_session_end.py",
        ".qoder/hooks/task_session_start.py",
        ".qoder/agents/distill-worker.md",
    }
    for name in HOOK_FILES:
        assert not (hooks_dir / name).exists()
    assert not (agents_dir / AGENT_FILE).exists()
    assert (hooks_dir / "other_tool.py").is_file()
    assert (agents_dir / "other-worker.md").is_file()


def test_clean_flag_via_cli(tmp_path, fake_pkg):
    (tmp_path / ".qoder").mkdir()
    runner = CliRunner()
    first = runner.invoke(install_hooks, ["--repo-path", str(tmp_path), "--ide", "qoder"])
    assert first.exit_code == 0, first.output
    script = tmp_path / ".qoder" / "hooks" / "task_session_start.py"
    assert script.is_file()

    result = runner.invoke(
        install_hooks,
        ["--repo-path", str(tmp_path), "--ide", "qoder", "--mode", "prompt", "--clean"],
    )
    assert result.exit_code == 0, result.output
    assert not script.is_file()
    assert "cleaned" in result.output