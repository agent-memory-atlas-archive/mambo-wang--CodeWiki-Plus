"""票 07：{宿主 × 档位 × 叠加} 接线矩阵——产物快照、非法组合、幂等、零回归锚点。

依据 docs/接线档位选择设计方案.md §3.1（两轴正交）、§3.2（档位定义）、
§3.5（注册表单源）、§3.6（选择入口校验表）、§3.11（注入文件适配）、§3.12（决策树）
与 .scratch/active-settle-wiring/issues/07-matrix-tests-docs.md：

  - 宿主：codebuddy / trae / qwenwork / qoder / cursor（注册表 family、verified、
    默认 active_settle 见 codewiki/hooks.yaml）。
  - 档位：hook / prompt / auto；叠加：on / off / None（None = 注册表默认）。
  - 合法组合产物快照：hook 档含 settings 注册 + 脚本；prompt 档只动注入文件；
    on 渲染 CODEWIKI-ACTIVE-SETTLE 块；off 不渲染。
  - 非法组合：prompt 家族宿主（qwenwork）+ hook 档 → 拒绝（抛错 / 退出码 1）。
  - 幂等：每个合法组合连跑两次，产物逐字节不变。
  - 零回归锚点：codebuddy × auto × None（= off）与今日产物逐字节一致。

注：cursor 是注册表里的「理论支持」条目（family=cursor），但尚未进入
``IDE_SPECS``（cursor 家族的 hooks.json/camelCase 适配未实现），因此安装器
按未支持宿主拒绝——本测试如实覆盖该现状，不臆造接线能力。
"""

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from codewiki.cli.commands.install_hooks import install_hooks
from codewiki.cli.utils.ide_config import (
    AGENT_FILE,
    HOOK_FILES,
    IDE_SPECS,
    PROMPT_HOOK_CMD,
    IdeWiringError,
    install_for_ide,
)
from codewiki.mcp.prompts import (
    _ACTIVE_SETTLE_START,
    _TASK_MEMORY_AGENTS_START,
)
from codewiki.mcp.tools.hook_registry import (
    active_settle_of,
    inject_file_of,
    load_registry,
    support_matrix_markdown,
    wiring_of,
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

# 要覆盖的宿主（工单要求至少这 5 个）。
HOSTS = ("codebuddy", "trae", "qwenwork", "qoder", "cursor")
# 可由 install_for_ide 实际接线的宿主（cursor 未进 IDE_SPECS，见模块 docstring）。
INSTALLABLE = ("codebuddy", "trae", "qwenwork", "qoder")
# hook 档宿主（家族有 shell hook 机制）。
HOOK_HOSTS = ("codebuddy", "trae", "qoder")
# prompt 家族宿主。
PROMPT_FAMILY = ("qwenwork",)
OVERLAYS = (None, True, False)

# 合法 (宿主, 档位) 组合（prompt 家族 × hook 档非法，单独用例覆盖）。
LEGAL_MODE_COMBOS = (
    [("codebuddy", m) for m in ("hook", "prompt", "auto")]
    + [("qoder", m) for m in ("hook", "prompt", "auto")]
    + [("trae", m) for m in ("hook", "prompt", "auto")]
    + [("qwenwork", m) for m in ("prompt", "auto")]
)

# 今日 codebuddy（claude 家族）hook 档 settings.json 的已知契约——零回归锚点。
EXPECTED_CODEBUDDY_SETTINGS = {
    "hooks": {
        "SessionStart": [
            {
                "matcher": "startup",
                "hooks": [
                    {
                        "type": "command",
                        "command": 'python ".codebuddy/hooks/task_session_start.py"',
                        "timeout": 15,
                    }
                ],
            }
        ],
        "SessionEnd": [
            {
                "matcher": "other",
                "hooks": [
                    {
                        "type": "command",
                        "command": 'python ".codebuddy/hooks/capture_session_end.py"',
                        "timeout": 30,
                    }
                ],
            }
        ],
        "UserPromptSubmit": [
            {
                "matcher": "",
                "hooks": [
                    {"type": "command", "command": PROMPT_HOOK_CMD, "timeout": 10}
                ],
            }
        ],
    }
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
    """递归快照目录内容（相对路径 → 字节），用于产物快照与幂等比对。"""
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


def _expected_settle(ide: str, overlay):
    """叠加生效值：None = 注册表默认；显式布尔 = 覆盖。"""
    return active_settle_of(ide) if overlay is None else bool(overlay)


def _expected_wiring(ide: str, mode: str) -> str:
    """档位生效值：auto = 注册表判定；显式 mode 原样。"""
    return wiring_of(ide) if mode == "auto" else mode


def _spec_dir(ide: str):
    return (IDE_SPECS.get(ide) or {}).get("dir")


def _install(repo: Path, ide: str, mode: str, overlay):
    kwargs = {"mode": mode}
    if overlay is not None:
        kwargs["active_settle"] = overlay
    return install_for_ide(str(repo), ide, **kwargs)


# ---------------------------------------------------------------------------
# 注册表矩阵解析（口径 = 注册表单源）
# ---------------------------------------------------------------------------


def test_registry_matrix_resolution():
    """5 宿主的家族 / 支持等级 / 默认档位 / 默认叠加与注册表口径一致。"""
    expected = {
        # id: (family, verified, wiring, active_settle)
        "codebuddy": ("claude", True, "hook", False),
        "qoder": ("claude", True, "hook", False),
        "trae": ("trae", True, "hook", True),
        "qwenwork": ("prompt", True, "prompt", True),
        "cursor": ("cursor", False, "hook", False),
    }
    for aid, (fam, verified, wiring, settle) in expected.items():
        agent = next(a for a in load_registry()["agents"] if a["id"] == aid)
        assert agent["family"] == fam
        assert bool(agent["verified"]) is verified
        assert wiring_of(aid) == wiring
        assert active_settle_of(aid) is settle
        assert inject_file_of(aid) == "AGENTS.md"


def test_readme_support_matrix_matches_registry():
    """G3：README 宿主验证表 = 注册表生成的矩阵（单一来源，无第二处双源漂移）。"""
    readme = (
        Path(__file__).resolve().parents[1] / "README.md"
    ).read_text(encoding="utf-8")
    assert support_matrix_markdown() in readme


# ---------------------------------------------------------------------------
# 合法组合产物快照：{宿主 × 档位 × 叠加}
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("ide", HOOK_HOSTS)
@pytest.mark.parametrize("overlay", OVERLAYS, ids=lambda o: f"settle={o}")
def test_hook_mode_products(tmp_path, fake_pkg, ide, overlay):
    """hook 档：settings 注册 + 脚本 + subagent 就位；on 渲染块、off 不渲染。"""
    repo = tmp_path / "repo"
    repo.mkdir()
    result = _install(repo, ide, "hook", overlay)

    spec = IDE_SPECS[ide]
    settings_path = repo / spec["dir"] / spec["settings"]
    hooks_dir = repo / spec["dir"] / "hooks"
    agents_dir = repo / spec["dir"] / spec["agents_dir"]

    assert result["wiring"] == "hook"
    assert result["active_settle"] is _expected_settle(ide, overlay)
    assert result["settings_written"] is True
    # 脚本与 distill-worker 就位
    for name in HOOK_FILES:
        assert (hooks_dir / name).is_file()
    assert (agents_dir / AGENT_FILE).is_file()
    # settings 注册我们的命令（start 脚本 + python -m 入口）
    commands = _all_commands(_read_json(settings_path))
    assert any("task_session_start.py" in c for c in commands)
    assert PROMPT_HOOK_CMD in commands
    if ide == "trae":
        # trae 家族：hooks.json 顶层 version + Stop 事件（无 SessionEnd）
        data = _read_json(settings_path)
        assert data.get("version") == 1
        assert "Stop" in data["hooks"]
    # 注入文件：共享引导块恒在；叠加按生效值渲染
    inject_text = (repo / inject_file_of(ide)).read_text(encoding="utf-8")
    assert _TASK_MEMORY_AGENTS_START in inject_text
    if _expected_settle(ide, overlay):
        assert _ACTIVE_SETTLE_START in inject_text
    else:
        assert _ACTIVE_SETTLE_START not in inject_text


@pytest.mark.parametrize("ide", ("codebuddy", "qoder", "trae", "qwenwork"))
@pytest.mark.parametrize("overlay", OVERLAYS, ids=lambda o: f"settle={o}")
def test_prompt_mode_only_touches_inject_file(tmp_path, fake_pkg, ide, overlay):
    """prompt 档：不建配置目录、不拷脚本、不写 settings，只动注入文件。"""
    repo = tmp_path / "repo"
    repo.mkdir()
    result = _install(repo, ide, "prompt", overlay)

    assert result["wiring"] == "prompt"
    assert result["active_settle"] is _expected_settle(ide, overlay)
    assert result["settings_written"] is False
    # 唯一产物：注入文件（+ 按生效值渲染的协议块）
    assert set(_snapshot(repo)) == {inject_file_of(ide)}
    assert _spec_dir(ide) is None or not (repo / _spec_dir(ide)).exists()
    inject_text = (repo / inject_file_of(ide)).read_text(encoding="utf-8")
    assert _TASK_MEMORY_AGENTS_START in inject_text
    if _expected_settle(ide, overlay):
        assert _ACTIVE_SETTLE_START in inject_text
    else:
        assert _ACTIVE_SETTLE_START not in inject_text


@pytest.mark.parametrize("ide", INSTALLABLE)
@pytest.mark.parametrize("overlay", OVERLAYS, ids=lambda o: f"settle={o}")
def test_auto_mode_equals_registry_resolved_mode(tmp_path, fake_pkg, ide, overlay):
    """auto 档 = 注册表判定档位：与显式解析档产物逐字节一致。"""
    repo_auto = tmp_path / "auto"
    repo_explicit = tmp_path / "explicit"
    repo_auto.mkdir()
    repo_explicit.mkdir()

    r_auto = _install(repo_auto, ide, "auto", overlay)
    r_explicit = _install(repo_explicit, ide, wiring_of(ide), overlay)

    assert r_auto["wiring"] == wiring_of(ide)
    assert _snapshot(repo_auto) == _snapshot(repo_explicit)
    assert r_auto["active_settle"] == r_explicit["active_settle"]


# ---------------------------------------------------------------------------
# 非法组合：prompt 家族 × hook 档 → 拒绝（不静默降级）
# ---------------------------------------------------------------------------


def test_qwenwork_hook_mode_rejected_by_install(tmp_path, fake_pkg):
    """prompt 家族宿主没有 shell hook：install_for_ide 兜底抛错，且不写任何文件。"""
    repo = tmp_path / "repo"
    repo.mkdir()
    with pytest.raises(IdeWiringError) as exc:
        install_for_ide(str(repo), "qwenwork", mode="hook")
    assert "prompt" in str(exc.value)
    assert _snapshot(repo) == {}  # 硬报错：无任何写入


def test_qwenwork_hook_mode_cli_exits_1(tmp_path):
    """CLI 非法组合：退出码 1 + 可执行建议（--mode prompt），注入文件原样。"""
    repo = tmp_path / "repo"
    repo.mkdir()
    agents = repo / inject_file_of("qwenwork")
    agents.write_text("# Project\n", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(
        install_hooks,
        ["--repo-path", str(repo), "--ide", "qwenwork", "--mode", "hook"],
    )
    assert result.exit_code == 1, result.output
    assert "--mode prompt" in result.output
    assert agents.read_text(encoding="utf-8") == "# Project\n"


def test_cursor_not_installable_but_present_in_registry(tmp_path):
    """cursor 是注册表「理论支持」条目，但尚未进入 IDE_SPECS：安装器拒绝。

    诚实覆盖现状：不臆造 cursor 家族的 hooks.json/camelCase 适配能力。
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    with pytest.raises(IdeWiringError) as exc:
        install_for_ide(str(repo), "cursor")
    assert "Unknown IDE" in str(exc.value)
    assert _snapshot(repo) == {}

    # CLI 的 --ide 取自 IDE_SPECS，cursor 不在其中 → 参数校验失败（非 0 退出）
    runner = CliRunner()
    result = runner.invoke(
        install_hooks, ["--repo-path", str(repo), "--ide", "cursor"]
    )
    assert result.exit_code != 0


# ---------------------------------------------------------------------------
# 幂等：每个合法组合连跑两次 = 跑一次（产物逐字节不变）
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "ide,mode",
    LEGAL_MODE_COMBOS,
    ids=[f"{i}-{m}" for i, m in LEGAL_MODE_COMBOS],
)
@pytest.mark.parametrize("overlay", OVERLAYS, ids=lambda o: f"settle={o}")
def test_install_twice_is_byte_identical(tmp_path, fake_pkg, ide, mode, overlay):
    repo = tmp_path / "repo"
    repo.mkdir()
    _install(repo, ide, mode, overlay)
    first = _snapshot(repo)
    _install(repo, ide, mode, overlay)
    assert _snapshot(repo) == first


# ---------------------------------------------------------------------------
# 零回归锚点：codebuddy × auto × None（= off）与今日产物逐字节一致
# ---------------------------------------------------------------------------


def test_zero_regression_codebuddy_auto_off(tmp_path, fake_pkg):
    """不传新参数（今日默认）与显式 auto+off 逐字节一致，且 settings 结构 = 今日契约。"""
    repo_today = tmp_path / "today"
    repo_explicit = tmp_path / "explicit"
    repo_today.mkdir()
    repo_explicit.mkdir()

    # 今日行为 = 不传 mode/active_settle
    install_for_ide(str(repo_today), "codebuddy")
    install_for_ide(str(repo_explicit), "codebuddy", mode="auto", active_settle=False)

    assert _snapshot(repo_today) == _snapshot(repo_explicit)
    # settings.json 结构等于今日已知契约（零回归锚点，非仅自比较）
    assert _read_json(repo_today / ".codebuddy" / "settings.json") == (
        EXPECTED_CODEBUDDY_SETTINGS
    )
    # off（= 注册表默认）不渲染主动沉淀块；共享引导块恒在
    text = (repo_today / "AGENTS.md").read_text(encoding="utf-8")
    assert _TASK_MEMORY_AGENTS_START in text
    assert _ACTIVE_SETTLE_START not in text