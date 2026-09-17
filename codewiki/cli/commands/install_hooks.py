"""
Install-hooks command for CodeWiki CLI.

用户触发创建/启用 hook 时自动检测项目根目录存在的智能体配置目录
（.codebuddy/.qoder/.claude/.gemini/.trae），检测到哪些就为哪些智能体接线——
拷贝 hook 脚本与 distill-worker subagent、合并 settings.json（TRAE 为
.trae/hooks.json，SessionEnd 映射为 Stop 事件）hook 注册、
写入 AGENTS.md 任务记忆引导段。千问办公（QwenWork）无 shell hook 机制，
走 prompt 接线（AGENTS.md 协议段，Agent 中介捕获），仅显式 --ide qwenwork
触发（仓库无标记目录，不参与自动检测）。

档位/叠加选择入口（见 docs/接线档位选择设计方案.md §3.6）：
--mode hook|prompt|auto（默认 auto = 按 hooks.yaml 注册表判定，与今日一致）、
--active-settle on|off（覆盖注册表默认）、--status（只读状态表）、
--inject-file（覆盖注入文件路径）、--clean（换档 prompt 时删除我们的脚本与
distill-worker.md，设计方案 §3.10）。
"""

import json
import sys
from pathlib import Path
from typing import Iterator, Optional

import click

from codewiki.cli.utils.errors import handle_error
from codewiki.cli.utils.ide_config import (
    END_HOOK_CMD,
    IDE_SPECS,
    START_HOOK_CMD,
    IdeWiringError,
    _relative_hook_suffix,
    detect_ide_dirs,
    install_for_ide,
)
from codewiki.mcp.prompts import _ACTIVE_SETTLE_START, _QWENWORK_CAPTURE_START
from codewiki.mcp.tools.hook_registry import (
    active_settle_of,
    get_agent,
    inject_file_of,
    load_registry,
    wiring_of,
)


def _echo_summary(repo: str, results: list[dict]) -> None:
    """输出每个 IDE 的接线结果摘要（仅用 ASCII 符号，兼容 Windows GBK 控制台）。"""
    click.echo()
    click.secho(f"Target repo: {repo}", fg="blue", bold=True)
    for r in results:
        if r.get("wiring") == "prompt":
            # prompt 模式（千问办公）：无目录/脚本/注册，只有 AGENTS.md 协议段
            click.secho(f"\n[{r['ide']}] -> AGENTS.md (prompt wiring)", fg="cyan", bold=True)
            # 换档清理报告（设计方案 §3.10）：移除的注册条目与删除的产物
            if r.get("unwired"):
                click.secho("  [unwired] removed CodeWiki hook registrations", fg="green")
            for path in r.get("cleaned") or []:
                click.secho(f"  [cleaned] {path}", fg="green")
            if r.get("protocol_changed"):
                click.secho("  [updated] AGENTS.md QwenWork capture protocol", fg="green")
            else:
                click.echo("  [no-change] AGENTS.md QwenWork capture protocol present")
            if r["agents_changed"]:
                click.secho("  [updated] AGENTS.md task-memory section", fg="green")
            else:
                click.echo("  [no-change] AGENTS.md task-memory section present")
            continue
        click.secho(f"\n[{r['ide']}] -> {r['dir']}/", fg="cyan", bold=True)
        for copied in r["copied"]:
            click.echo(f"  [copied] {copied}")
        if r["settings_written"]:
            # 文件名跟随家族（claude 家族 settings.json / trae 家族 hooks.json）
            settings_file = r.get("settings_file") or "settings.json"
            if r["settings_changed"]:
                click.secho(f"  [updated] {settings_file}", fg="green")
            else:
                click.echo(f"  [no-change] {settings_file} already wired")
        if r["agents_changed"]:
            click.secho("  [updated] AGENTS.md task-memory section", fg="green")
        else:
            click.echo("  [no-change] AGENTS.md task-memory section present")
    click.secho("\nHook wiring complete.", fg="green", bold=True)


# ---------------------------------------------------------------------------
# --status（只读）：设计方案 §3.6 入口 3 的状态表
# ---------------------------------------------------------------------------

# 各家族的已知能力缺口（与 hooks.yaml 家族注释口径一致；仅展示用）。
# 缺口是家族层事实，与某个仓库是否已接线无关。
_STATUS_FAMILY_GAPS = {
    # prompt 家族：宿主无 shell hook，采集全靠 Agent 中介执行协议段
    "prompt": "no auto-capture; agent-mediated",
    # trae 家族：无 SessionEnd、Stop 不携带 transcript → 保险采集 + 主动沉淀补
    "trae": "no SessionEnd -> 保险采集+主动沉淀",
    # cursor 家族：无 SessionEnd 等价事件，会话正文无采集（采集降级）
    "cursor": "no SessionEnd -> 采集降级",
}


def _iter_settings_commands(settings_path: Path) -> Iterator[str]:
    """枚举 settings.json / hooks.json 里所有已注册的 hook command（只读）。

    文件不存在或损坏时产出为空——状态表把这种情况记为 not wired，不抛错。
    """
    if not settings_path.is_file():
        return
    try:
        data = json.loads(settings_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    hooks = data.get("hooks") if isinstance(data, dict) else None
    if not isinstance(hooks, dict):
        return
    for entries in hooks.values():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            for h in entry.get("hooks") or []:
                if isinstance(h, dict) and isinstance(h.get("command"), str):
                    yield h["command"]


def _wired_on_disk(repo_path: Path, agent: dict) -> str:
    """反匹配某宿主在磁盘上的实际接线状态（未接线返回 ``not wired``）。

    hook 档用 ``ide_config._relative_hook_suffix`` 口径：以期望命令结尾的
    相对脚本后缀（归一化路径分隔符后）匹配已注册命令，兼容历史旧格式条目。
    prompt 档没有配置文件，"接线" = 注入文件里有我们的标记块。只读，绝不
    修改任何文件。
    """
    agent_id = str(agent.get("id", ""))
    spec = IDE_SPECS.get(agent_id) or {}
    ide_dir = spec.get("dir")
    if not ide_dir:
        # 无配置目录的宿主：仅 prompt 档可接线（注入文件标记块反查）
        if wiring_of(agent_id) != "prompt":
            return "not wired"
        inject = repo_path / inject_file_of(agent_id)
        try:
            text = inject.read_text(encoding="utf-8") if inject.is_file() else ""
        except OSError:
            text = ""
        # 只认专属协议块：共享引导块（TEAM-MEMORY-TASK）hook 档也会写，
        # 不构成 prompt 接线的证据。新块（CODEWIKI-ACTIVE-SETTLE）泛化取代
        # 旧块（CODEWIKI-QWENWORK），迁移前后都算已接线；旧块仅存在于
        # 未迁移的历史仓库。
        if _ACTIVE_SETTLE_START in text or _QWENWORK_CAPTURE_START in text:
            return "AGENTS.md only"
        return "not wired"

    settings_path = repo_path / ide_dir / str(spec.get("settings", "settings.json"))
    commands = list(_iter_settings_commands(settings_path))
    if not commands:
        return "not wired"

    def norm(cmd: str) -> str:
        # Windows 下反斜杠/正斜杠等价，与 merge_settings_json 的去重口径一致
        return cmd.replace("\\", "/")

    start_suffix = _relative_hook_suffix(START_HOOK_CMD.format(ide_dir=ide_dir))
    end_suffix = _relative_hook_suffix(END_HOOK_CMD.format(ide_dir=ide_dir))
    has_start = bool(start_suffix) and any(norm(c).endswith(start_suffix) for c in commands)
    has_end = bool(end_suffix) and any(norm(c).endswith(end_suffix) for c in commands)
    if not (has_start or has_end):
        return "not wired"
    if str(agent.get("family", "")) == "trae":
        # TRAE：Stop 不携带 transcript，收尾注册仅诊断意义（表样见设计方案 §3.6）
        return "hooks(仅SS)+AGENTS"
    if has_start and has_end:
        return "hooks+settings"
    return "hooks(partial)+settings"


def _echo_status(repo_path: Path, settle_override: Optional[bool]) -> None:
    """打印接线状态表（只读；不修改任何文件，调用方保证退出码 0）。

    列口径对齐设计方案 §3.6 表样；``registry`` 列复用
    ``support_matrix_markdown()`` 的"已验证/理论支持"口径，保证与 README 一致；
    ``active_settle`` 列展示生效值并标注来源（注册表默认 / CLI 覆盖）。
    """
    lines = [
        "| agent | family | registry | wiring | active_settle | wired-on-disk | capability gap |",
        "|---|---|---|---|---|---|---|",
    ]
    agents = load_registry().get("agents", [])
    # 行序与 support_matrix_markdown 一致：已验证优先，其余按字母序
    ordered = sorted(agents, key=lambda a: (not bool(a.get("verified")), str(a.get("id", ""))))
    for agent in ordered:
        agent_id = str(agent.get("id", "?"))
        family = str(agent.get("family", "?"))
        registry = "已验证" if agent.get("verified") else "理论支持"
        wiring = wiring_of(agent_id)
        if settle_override is None:
            settle_text = ("on" if active_settle_of(agent_id) else "off") + "(默认)"
        else:
            settle_text = ("on" if settle_override else "off") + "(CLI)"
        disk = _wired_on_disk(repo_path, agent)
        gap = _STATUS_FAMILY_GAPS.get(family, "-")
        lines.append(
            f"| {agent_id} | {family} | {registry} | {wiring} | {settle_text} | {disk} | {gap} |"
        )
    click.echo("\n".join(lines))


@click.command(name="install-hooks")
@click.option(
    "--ide",
    type=click.Choice(list(IDE_SPECS), case_sensitive=False),
    default=None,
    help=(
        "Wire a specific IDE only, skipping auto-detection. One of: "
        + ", ".join(IDE_SPECS)
        + ". The IDE's config dir must already exist; pass --create-dir to"
        " create it."
    ),
)
@click.option(
    "--mode",
    type=click.Choice(["hook", "prompt", "auto"], case_sensitive=False),
    default="auto",
    show_default=True,
    help=(
        "Wiring tier: hook (shell hooks: scripts + settings), prompt (inject"
        " file only, no config dir/scripts/settings), auto (follow the"
        " hooks.yaml registry; today's behavior). Invalid combinations are"
        " hard errors, never silent downgrades."
    ),
)
@click.option(
    "--active-settle",
    "active_settle",
    type=click.Choice(["on", "off"], case_sensitive=False),
    default=None,
    help=(
        "Override the registry's active-settle default for this run (whether"
        " the ACTIVE-SETTLE protocol block applies). Omit to keep the"
        " registry default."
    ),
)
@click.option(
    "--status",
    "status",
    is_flag=True,
    default=False,
    help=(
        "Print a read-only status table (agent / family / registry / wiring /"
        " active_settle / wired-on-disk / capability gap). Never modifies any"
        " file; exits 0."
    ),
)
@click.option(
    "--inject-file",
    "inject_file",
    type=click.Path(),
    default=None,
    help=(
        "Override the inject file path (repo-relative; default: registry"
        " inject_file_of, normally AGENTS.md)."
    ),
)
@click.option(
    "--clean",
    is_flag=True,
    default=False,
    help=(
        "When switching to prompt wiring, also delete CodeWiki-owned physical"
        " artifacts (our .py hook scripts under <config_dir>/hooks/ and"
        " distill-worker.md). Without this flag the files are kept so a"
        " switch back to hook wiring can reuse them. Only our own files are"
        " ever removed; other tools' hooks are untouched."
    ),
)
@click.option(
    "--create-dir",
    "create_dir",
    is_flag=True,
    default=False,
    help=(
        "With --ide only: allow wiring an IDE whose config dir does not"
        " exist yet in the repo (the dir will be created). Safety gate:"
        " without this flag, --ide never conjures new IDE config dirs."
    ),
)
@click.option(
    "--repo-path",
    type=click.Path(),
    default=".",
    help="Target project path (default: current directory)",
)
def install_hooks(
    ide: Optional[str],
    mode: str,
    active_settle: Optional[str],
    status: bool,
    inject_file: Optional[str],
    clean: bool,
    create_dir: bool,
    repo_path: str,
) -> None:
    """
    Wire CodeWiki task-memory hooks/subagents for detected IDEs.

    无 --ide 参数时自动检测项目根目录存在的智能体配置目录
    （.codebuddy/.qoder/.claude/.gemini/.trae），检测到哪些就为哪些接线。
    每个 IDE 接线内容：强制拷贝 hook 脚本与 distill-worker subagent 到
    对应目录、幂等合并 settings.json 的 SessionStart/SessionEnd 采集注册 +
    UserPromptSubmit 技能草稿提示注册（advisory，见 skill-creator §10）、
    向 AGENTS.md upsert 任务记忆引导段（多 IDE 共享一份）。

    档位与叠加（设计方案 §3.6）：--mode 默认 auto（按注册表，与今日一致）；
    --mode hook 对 prompt 家族宿主（qwenwork）硬报错；--mode prompt 只动
    注入文件；--active-settle 覆盖注册表默认；--status 先看后选。

    Examples:

    \b
    # Auto-detect IDEs in the current project and wire all found
    $ codewiki install-hooks

    \b
    # Auto-detect in a specific project
    $ codewiki install-hooks --repo-path /path/to/project

    \b
    # Wire a specific IDE only (skip detection)
    $ codewiki install-hooks --ide qoder

    \b
    # Inspect wiring status first (read-only), then choose mode/overlay
    $ codewiki install-hooks --status
    $ codewiki install-hooks --ide trae --mode hook --active-settle on
    """
    try:
        # --active-settle on|off → 布尔；None = 不覆盖，用注册表默认
        settle = None if active_settle is None else active_settle.lower() == "on"

        if status:
            # 只读状态表：不修改任何文件，始终退出码 0
            _echo_status(Path(repo_path), settle)
            sys.exit(0)

        if ide:
            target = ide.lower()
            spec = IDE_SPECS[target]
            # prompt 档不建/不动配置目录，故也不要求目录存在
            if spec.get("dir") and not create_dir and mode != "prompt":
                ide_dir = Path(repo_path) / spec["dir"]
                if not ide_dir.is_dir():
                    raise IdeWiringError(
                        f"target dir {spec['dir']}/ does not exist in {repo_path}. "
                        "Explicit --ide wiring does not create missing IDE config "
                        "dirs (a repo should only be wired for tools actually "
                        "used in it). Re-run with --create-dir if you really "
                        f"want to wire {target} into this repo."
                    )
            targets = [target]
        else:
            if create_dir:
                raise IdeWiringError("--create-dir only makes sense together with --ide <name>.")
            targets = detect_ide_dirs(repo_path)
        if not targets:
            click.secho(
                "No supported IDE config dir detected in the project root.",
                fg="yellow",
            )
            # 提示从 IDE_SPECS 动态生成：新增 IDE 只需在注册表加一行，
            # 此处自动跟随（不再需要同步修改硬编码列表）。
            click.echo(
                "Detected dirs: "
                + " / ".join(spec["dir"] for spec in IDE_SPECS.values() if spec.get("dir"))
            )
            click.echo(
                "QwenWork (prompt wiring) has no repo marker and is never"
                " auto-detected - wire it explicitly with --ide qwenwork"
            )
            click.echo(
                "To wire a specific IDE whose config dir already exists, use: "
                "codewiki install-hooks --ide <" + "|".join(IDE_SPECS) + ">"
            )
            click.echo(
                "(--ide requires the IDE config dir to exist; add --create-dir"
                " only if you deliberately want to create it)"
            )
            sys.exit(0)

        # 校验硬报错（不静默降级）：prompt 家族宿主没有 shell hook 机制，
        # --mode hook 是非法组合（--mode auto 走注册表判定，不受此限）。
        if mode == "hook":
            for name in targets:
                if wiring_of(name) == "prompt":
                    raise IdeWiringError(
                        f"{name} 无 shell hook 机制（注册表为 prompt 家族），"
                        "不能用 --mode hook 接线，请用 --mode prompt"
                    )

        results = []
        for name in targets:
            if mode == "hook":
                # 理论支持宿主：接线照做，但必须打黄色警告（不静默降级）
                agent_entry = get_agent(name) or {}
                if not agent_entry.get("verified", False):
                    click.secho(
                        f"[{name}] warning: registry verified=false"
                        "（家族归并推导，未经真机验证）——接线后请跑模拟事件验证",
                        fg="yellow",
                    )
            results.append(
                install_for_ide(
                    repo_path,
                    name,
                    mode=mode,
                    active_settle=settle,
                    clean=clean,
                    inject_file=inject_file,
                )
            )
        _echo_summary(repo_path, results)
    except IdeWiringError as e:
        click.secho(f"\nError: hook wiring failed: {e}", fg="red", err=True)
        sys.exit(1)
    except Exception as e:
        sys.exit(handle_error(e))
