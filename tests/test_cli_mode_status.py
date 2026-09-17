"""票 03：CLI --mode / --active-settle / --status / --inject-file / --clean。

依据 docs/接线档位选择设计方案.md §3.6 与 .scratch/active-settle-wiring/issues/03：
  - --mode hook + prompt 家族宿主（qwenwork）→ 退出码 1 + 建议改用 --mode prompt
  - --mode hook + verified: false → 接线成功 + 黄色警告
  - --mode prompt → 只动注入文件（不建配置目录、不拷脚本、不写 settings）
  - --mode auto → 与今日行为一致（零回归：产物逐字节一致）
  - --active-settle on|off 覆盖注册表默认并透传给安装逻辑
  - --status → 只读状态表，含全部七列，退出码 0，不改任何文件
  - --inject-file / --clean 参数可达
"""

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from codewiki.cli.commands.install_hooks import install_hooks, _wired_on_disk
from codewiki.cli.utils.ide_config import AGENT_FILE, HOOK_FILES, install_for_ide
from codewiki.mcp.prompts import (
    _ACTIVE_SETTLE_START,
    _TASK_MEMORY_AGENTS_START,
)

HOOK_SOURCES = {
    "capture_session_end.py": "import json\n\nprint('ok')\n",
    "task_session_start.py": "import os\n\nprint('ok')\n",
}
AGENT_SOURCE = (
    "---\nname: distill-worker\nmcpServers:\n  - codewiki\n---\nworker\n"
)
AGENT_SOURCE_CLAUDE = (
    "---\nname: distill-worker\n"
    "tools: Read, Write, mcp__codewiki__distill_conversation\n---\nworker\n"
)


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
    """递归快照目录内容（相对路径 → 字节），用于零回归逐字节比对。"""
    return {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


# ---------------------------------------------------------------------------
# --mode hook 校验（不静默降级）
# ---------------------------------------------------------------------------


def test_mode_hook_on_qwenwork_exits_1_with_prompt_suggestion(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "AGENTS.md").write_text("# Project\n", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(
        install_hooks,
        ["--repo-path", str(repo), "--ide", "qwenwork", "--mode", "hook"],
    )
    assert result.exit_code == 1, result.output
    assert "--mode prompt" in result.output  # 可执行建议
    # 硬报错：注入文件原样，无任何写入
    assert (repo / "AGENTS.md").read_text(encoding="utf-8") == "# Project\n"


def test_mode_hook_on_verified_false_warns_but_wires(tmp_path, fake_pkg, monkeypatch):
    # 理论支持宿主（注册表 verified: false）：接线成功 + 黄色警告。
    # 现注册表里可接线宿主均已验证，故把 gemini-cli 临时翻成未验证。
    import copy

    from codewiki.mcp.tools import hook_registry as hr

    patched = copy.deepcopy(hr.load_registry())
    for a in patched["agents"]:
        if a["id"] == "gemini-cli":
            a["verified"] = False
    monkeypatch.setattr(hr, "load_registry", lambda: patched)

    (tmp_path / ".gemini").mkdir()
    runner = CliRunner()
    result = runner.invoke(
        install_hooks,
        ["--repo-path", str(tmp_path), "--ide", "gemini-cli", "--mode", "hook"],
    )
    assert result.exit_code == 0, result.output
    assert "warning" in result.output and "verified=false" in result.output
    assert (tmp_path / ".gemini" / "settings.json").is_file()


def test_mode_hook_on_verified_host_has_no_warning(tmp_path, fake_pkg):
    (tmp_path / ".codebuddy").mkdir()
    runner = CliRunner()
    result = runner.invoke(
        install_hooks,
        ["--repo-path", str(tmp_path), "--ide", "codebuddy", "--mode", "hook"],
    )
    assert result.exit_code == 0, result.output
    assert "warning" not in result.output


# ---------------------------------------------------------------------------
# --mode prompt：只动注入文件
# ---------------------------------------------------------------------------


def test_mode_prompt_codebuddy_touches_no_config_dir(tmp_path, fake_pkg):
    # 工单验收：--mode prompt 不产生 .codebuddy/ 变更（不拷脚本不写 settings）
    (tmp_path / ".codebuddy").mkdir()
    (tmp_path / ".codebuddy" / "settings.json").write_text(
        json.dumps({"telemetry": {"enabled": True}}), encoding="utf-8"
    )
    before = _snapshot(tmp_path)

    runner = CliRunner()
    result = runner.invoke(
        install_hooks,
        ["--repo-path", str(tmp_path), "--ide", "codebuddy", "--mode", "prompt"],
    )
    assert result.exit_code == 0, result.output
    assert "prompt wiring" in result.output
    # .codebuddy/ 内容逐字节不变（无脚本拷贝、无 settings 改写）
    settings_after = (tmp_path / ".codebuddy" / "settings.json").read_bytes()
    assert settings_after == before[".codebuddy/settings.json"]
    assert not (tmp_path / ".codebuddy" / "hooks").exists()
    assert not (tmp_path / ".codebuddy" / "agents").exists()
    # 唯一产物：AGENTS.md 的注入块
    text = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert _TASK_MEMORY_AGENTS_START in text


def test_mode_prompt_skips_create_dir_gate(tmp_path):
    # prompt 档不建目录，也就不受"目录必须存在"闸门约束
    runner = CliRunner()
    result = runner.invoke(
        install_hooks,
        ["--repo-path", str(tmp_path), "--ide", "codebuddy", "--mode", "prompt"],
    )
    assert result.exit_code == 0, result.output
    assert not (tmp_path / ".codebuddy").exists()


# ---------------------------------------------------------------------------
# --mode auto：零回归（与今日行为逐字节一致）
# ---------------------------------------------------------------------------


def test_mode_auto_is_byte_identical_to_default(tmp_path, fake_pkg):
    # 两个构造一致的仓库：一个跑默认（不传新参数），一个跑显式 --mode auto，
    # 产物逐字节一致 = 零回归。
    repo_a = tmp_path / "a"
    repo_b = tmp_path / "b"
    for repo in (repo_a, repo_b):
        (repo / ".codebuddy").mkdir(parents=True)
        (repo / ".trae").mkdir()

    runner = CliRunner()
    default_run = runner.invoke(install_hooks, ["--repo-path", str(repo_a)])
    assert default_run.exit_code == 0, default_run.output
    auto_run = runner.invoke(
        install_hooks, ["--repo-path", str(repo_b), "--mode", "auto"]
    )
    assert auto_run.exit_code == 0, auto_run.output
    snap_a = {rel: data for rel, data in _snapshot(repo_a).items()}
    snap_b = {rel: data for rel, data in _snapshot(repo_b).items()}
    assert snap_a == snap_b  # 逐字节一致


def test_mode_auto_qwenwork_still_prompt(tmp_path):
    # auto 对 qwenwork 走注册表判定的 prompt 档（今日行为）
    repo = tmp_path / "repo"
    repo.mkdir()
    runner = CliRunner()
    result = runner.invoke(
        install_hooks, ["--repo-path", str(repo), "--ide", "qwenwork", "--mode", "auto"]
    )
    assert result.exit_code == 0, result.output
    text = (repo / "AGENTS.md").read_text(encoding="utf-8")
    assert _ACTIVE_SETTLE_START in text


# ---------------------------------------------------------------------------
# --active-settle：覆盖注册表默认并透传
# ---------------------------------------------------------------------------


def test_active_settle_override_reaches_install_logic(tmp_path, fake_pkg):
    (tmp_path / ".codebuddy").mkdir()
    runner = CliRunner()
    result = runner.invoke(
        install_hooks,
        ["--repo-path", str(tmp_path), "--ide", "codebuddy", "--active-settle", "on"],
    )
    assert result.exit_code == 0, result.output
    # 直接调安装入口验证覆盖生效（注册表默认 codebuddy 为 off）
    r = install_for_ide(str(tmp_path), "codebuddy", active_settle=True)
    assert r["active_settle"] is True
    r2 = install_for_ide(str(tmp_path), "trae", mode="hook", active_settle=False)
    assert r2["active_settle"] is False  # trae 注册表默认 on，被显式覆盖为 off


def test_active_settle_default_from_registry(tmp_path, fake_pkg):
    # 不传覆盖 → 安装结果摘要里的生效值 = 注册表默认（codebuddy off / trae on）
    r1 = install_for_ide(str(tmp_path), "codebuddy")
    assert r1["active_settle"] is False
    r2 = install_for_ide(str(tmp_path), "trae", mode="hook")
    assert r2["active_settle"] is True


# ---------------------------------------------------------------------------
# --status：只读状态表
# ---------------------------------------------------------------------------


def test_status_table_header_columns(tmp_path, fake_pkg):
    runner = CliRunner()
    result = runner.invoke(install_hooks, ["--repo-path", str(tmp_path), "--status"])
    assert result.exit_code == 0, result.output
    header = result.output.splitlines()[0]
    # 七列表头（工单验收至少三列：agent / registry / wiring 均在其中）
    for col in ("agent", "family", "registry", "wiring", "active_settle",
                "wired-on-disk", "capability gap"):
        assert col in header, f"missing column: {col}"


def test_status_source_annotation_default_vs_cli(tmp_path):
    runner = CliRunner()
    default = runner.invoke(install_hooks, ["--repo-path", str(tmp_path), "--status"])
    assert default.exit_code == 0
    assert "(默认)" in default.output  # 注册表默认来源标注
    override = runner.invoke(
        install_hooks,
        ["--repo-path", str(tmp_path), "--status", "--active-settle", "on"],
    )
    assert override.exit_code == 0
    assert "(CLI)" in override.output  # CLI 覆盖来源标注
    assert "(默认)" not in override.output


def test_status_is_readonly_and_exit_0(tmp_path, fake_pkg):
    (tmp_path / ".codebuddy").mkdir()
    before = _snapshot(tmp_path)
    runner = CliRunner()
    result = runner.invoke(install_hooks, ["--repo-path", str(tmp_path), "--status"])
    assert result.exit_code == 0
    assert _snapshot(tmp_path) == before  # 不改任何文件
    assert "Hook wiring complete" not in result.output  # 未执行接线


def test_status_wired_on_disk_reflects_reality(tmp_path, fake_pkg):
    (tmp_path / ".codebuddy").mkdir()
    runner = CliRunner()
    before = runner.invoke(install_hooks, ["--repo-path", str(tmp_path), "--status"])
    assert "not wired" in before.output

    runner.invoke(install_hooks, ["--repo-path", str(tmp_path)])
    after = runner.invoke(install_hooks, ["--repo-path", str(tmp_path), "--status"])
    assert after.exit_code == 0
    # codebuddy 接线后应显示 hooks+settings；qwenwork 仍为 not wired
    cb_row = next(l for l in after.output.splitlines() if l.startswith("| codebuddy"))
    assert "hooks+settings" in cb_row
    qw_row = next(l for l in after.output.splitlines() if l.startswith("| qwenwork"))
    assert "not wired" in qw_row
    assert "AGENTS.md only" not in qw_row


def test_status_wired_on_disk_matches_legacy_backslash_entries(tmp_path):
    # 反匹配用 _relative_hook_suffix 口径：反斜杠历史条目也算已接线
    (tmp_path / ".qoder").mkdir()
    (tmp_path / ".qoder" / "settings.json").write_text(
        json.dumps(
            {
                "hooks": {
                    "SessionStart": [
                        {
                            "matcher": "startup",
                            "hooks": [
                                {
                                    "type": "command",
                                    "command": 'python "D:\\repos\\proj\\.qoder\\hooks\\task_session_start.py"',
                                    "timeout": 15,
                                }
                            ],
                        }
                    ]
                }
            }
        ),
        encoding="utf-8",
    )
    agent = {"id": "qoder", "family": "claude"}
    assert _wired_on_disk(tmp_path, agent) != "not wired"


def test_status_gap_column_has_family_gaps(tmp_path):
    runner = CliRunner()
    result = runner.invoke(install_hooks, ["--repo-path", str(tmp_path), "--status"])
    qw_row = next(l for l in result.output.splitlines() if l.startswith("| qwenwork"))
    assert "no auto-capture; agent-mediated" in qw_row
    tr_row = next(l for l in result.output.splitlines() if l.startswith("| trae"))
    assert "no SessionEnd" in tr_row


# ---------------------------------------------------------------------------
# --inject-file / --clean：参数可达，不破坏现状
# ---------------------------------------------------------------------------


def test_inject_file_override_writes_custom_file(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    runner = CliRunner()
    result = runner.invoke(
        install_hooks,
        [
            "--repo-path", str(repo),
            "--ide", "qwenwork",
            "--mode", "prompt",
            "--inject-file", "docs/AGENT_INSTRUCTIONS.md",
        ],
    )
    assert result.exit_code == 0, result.output
    custom = repo / "docs" / "AGENT_INSTRUCTIONS.md"
    assert custom.is_file()
    assert _TASK_MEMORY_AGENTS_START in custom.read_text(encoding="utf-8")
    assert not (repo / "AGENTS.md").exists()  # 默认注入文件未被创建


def test_clean_flag_reachable_and_harmless(tmp_path, fake_pkg):
    (tmp_path / ".qoder").mkdir()
    runner = CliRunner()
    result = runner.invoke(
        install_hooks, ["--repo-path", str(tmp_path), "--ide", "qoder", "--clean"]
    )
    assert result.exit_code == 0, result.output
    # 现状不被破坏：脚本与 settings 正常接线（删除逻辑属票 05）
    assert (tmp_path / ".qoder" / "settings.json").is_file()
    for name in HOOK_FILES:
        assert (tmp_path / ".qoder" / "hooks" / name).is_file()
