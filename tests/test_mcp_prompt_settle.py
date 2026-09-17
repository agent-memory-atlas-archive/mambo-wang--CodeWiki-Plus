"""票 06：MCP prompt 同步——team-memory-hook 的 mode / active_settle / action=status。

依据 docs/接线档位选择设计方案.md §3.6 入口 2 与
.scratch/active-settle-wiring/issues/06：
  - mode=prompt + active_settle=on → 返回 prompt 档 + 主动沉淀指引，不含"需装 hook"
  - action=status → 含 `--status` 命令与能力缺口解读模板
  - 不传新参数 → 行为与今日一致（默认 hook 正文，向后兼容）
  - init-wiki enable_task_management 段补 prompt 档说明
  - 参数在 MCP 工具 schema/args 元组里登记
"""

from __future__ import annotations

import asyncio

from codewiki.mcp.prompts import (
    _PROMPT_REGISTRY,
    _prompt_init_wiki,
    _prompt_team_memory_hook,
    register,
)

_SETTLE_NOTE_HEAD = "**主动沉淀叠加（active_settle=on）**"


def _args(**kw):
    """默认带 repo_path；调用方可覆盖任意参数。"""
    base = {"repo_path": "."}
    base.update(kw)
    return base


class _FakeServer:
    """最小 MCP Server 桩：只捕获 list_prompts/get_prompt 注册的处理器。"""

    def __init__(self):
        self._list = None
        self._get = None

    def list_prompts(self):
        def deco(fn):
            self._list = fn
            return fn

        return deco

    def get_prompt(self):
        def deco(fn):
            self._get = fn
            return fn

        return deco


def _get_prompt(name: str, arguments: dict) -> str:
    """走真实 get_prompt 分发路径，返回响应正文。"""
    srv = _FakeServer()
    register(srv)
    result = asyncio.run(srv._get(name, arguments))
    return result.messages[0].content.text


# ---------------------------------------------------------------------------
# 1. mode=prompt + active_settle=on
# ---------------------------------------------------------------------------


def test_prompt_mode_on_via_get_prompt():
    # get_prompt 路径（非直接调私有函数），覆盖 args → 响应的完整接线
    text = _get_prompt(
        "team-memory-hook",
        {"action": "enable", "mode": "prompt", "active_settle": "on"},
    )
    assert "prompt 档" in text
    assert "--mode prompt" in text
    assert "--active-settle on" in text
    # 主动沉淀要点：停顿点四判据 + 保险采集说明
    assert "自然停顿点四判据" in text
    for criterion in ("里程碑", "关键决策", "话题转向", "收尾轮"):
        assert criterion in text
    assert "保险采集" in text
    assert "CODEWIKI-ACTIVE-SETTLE" in text


def test_prompt_mode_does_not_require_hook_install():
    text = _get_prompt(
        "team-memory-hook",
        {"action": "enable", "mode": "prompt", "active_settle": "on"},
    )
    # 验收硬项：prompt 档指引不得出现"需装 hook"类字样
    assert "需装 hook" not in text
    assert "需装 Hook" not in text
    assert "需要安装" not in text
    # prompt 档只写注入文件，不引导拷贝采集脚本
    assert "capture_session_end.py" not in text


def test_prompt_mode_off_renders_without_settle_note():
    text = _prompt_team_memory_hook(_args(action="enable", mode="prompt"))
    assert "prompt 档" in text
    assert "--mode prompt" in text
    # 未叠加时不追加 `--active-settle on`，也不出现叠加说明
    assert "--active-settle" not in text
    assert _SETTLE_NOTE_HEAD not in text


# ---------------------------------------------------------------------------
# 2. action=status
# ---------------------------------------------------------------------------


def test_status_action_has_command_and_gap_reading():
    text = _get_prompt("team-memory-hook", {"action": "status"})
    assert "codewiki install-hooks" in text
    assert "--status" in text
    # 缺口解读模板：gap 列 + 各家族缺口 + 决策模板
    assert "capability gap" in text
    assert "no auto-capture; agent-mediated" in text
    assert "no SessionEnd -> 保险采集+主动沉淀" in text
    assert "决策模板" in text
    # 逐列含义解释（不退化为一句空话）
    for col in ("agent", "family", "registry", "wiring", "active_settle", "wired-on-disk"):
        assert f"**{col}**" in text


def test_status_action_takes_priority_over_mode():
    # status 是独立动作：即便同时传 mode 也返回状态诊断而非接线正文
    text = _prompt_team_memory_hook(_args(action="status", mode="prompt"))
    assert "--status" in text
    assert "prompt 档是什么" not in text


# ---------------------------------------------------------------------------
# 3. 向后兼容：不传新参数 = 今日 hook 正文
# ---------------------------------------------------------------------------


def test_default_output_unchanged_without_new_params():
    default = _prompt_team_memory_hook(_args())
    auto = _prompt_team_memory_hook(_args(mode="auto"))
    hook = _prompt_team_memory_hook(_args(mode="hook"))
    # 未传 mode（或 auto/hook）都走原 hook 接线正文，逐字节一致
    assert default == auto == hook
    assert "对话自动采集 Hook" in default
    assert "install-hooks" in default
    assert "capture_session_end.py" in default
    assert "settings.json" in default
    assert "hooks.yaml" in default
    # 未叠加 active_settle 时不出现叠加说明（与今日一致）
    assert _SETTLE_NOTE_HEAD not in default


def test_enable_without_mode_matches_existing_behavior():
    text = _prompt_team_memory_hook(_args(action="enable"))
    assert "覆盖全部已探测" in text
    assert "settings.json" in text
    assert _SETTLE_NOTE_HEAD not in text


def test_invalid_mode_falls_back_to_auto():
    invalid = _prompt_team_memory_hook(_args(mode="bogus"))
    assert invalid == _prompt_team_memory_hook(_args())


# ---------------------------------------------------------------------------
# 4. init-wiki：enable_task_management 段补 prompt 档
# ---------------------------------------------------------------------------


def test_init_wiki_prompt_tier_note():
    text = _prompt_init_wiki(_args(enable_task_management="true"))
    assert "档位选择（mode）" in text
    assert "--mode prompt" in text
    assert "只写注入文件" in text
    # 原有守则未被破坏
    assert "绝不主动新建" in text


def test_init_wiki_off_has_no_tier_note():
    text = _prompt_init_wiki(_args())
    assert "档位选择（mode）" not in text


# ---------------------------------------------------------------------------
# 5. schema / args 元组登记
# ---------------------------------------------------------------------------


def test_team_memory_hook_args_registered():
    meta = next(m for m in _PROMPT_REGISTRY if m["name"] == "team-memory-hook")
    names = {n for n, _ in meta["args"]}
    assert {"action", "repo_path", "mode", "active_settle"} <= names


def test_init_wiki_registers_active_settle():
    meta = next(m for m in _PROMPT_REGISTRY if m["name"] == "init-wiki")
    names = {n for n, _ in meta["args"]}
    assert {"enable_task_management", "active_settle"} <= names