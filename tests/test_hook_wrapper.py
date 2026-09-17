"""Regression tests for codewiki/hooks/capture_session_end.py (the IDE hook wrapper).

The wrapper is copied verbatim into each project's ``.<ide>/hooks/`` directory and
run by the IDE on SessionEnd. It is fire-and-forget: it spawns the real capture in
a detached child and reports "started", so its stdout can never prove that
anything landed — ``repowiki/raw/`` is the only evidence.

That makes exactly one failure mode dangerous: a payload the wrapper cannot read.
It used to be swallowed (``_read_event`` returned ``{}``, the child was spawned
with no event file) while the wrapper still printed the success line, so a
miswired hook or a malformed event looked identical to a successful capture.
These tests pin the honest split:

1. unreadable / absent / empty stdin -> ``capture skipped: <reason>``, no child;
2. usable event -> forwarded to the child as a temp file, child detached,
   fire-and-forget line printed.
"""

from __future__ import annotations

import io
import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from codewiki.hooks import capture_session_end as wrapper  # noqa: E402


class _PipedStdin:
    """Piped native stdin: exposes a real ``.buffer`` of raw bytes."""

    def __init__(self, raw: bytes) -> None:
        self.buffer = io.BytesIO(raw)

    def isatty(self) -> bool:
        return False


class _TtyStdin:
    """Interactive invocation: no pipe behind stdin."""

    def __init__(self) -> None:
        self.buffer = io.BytesIO(b"")

    def isatty(self) -> bool:
        return True


@pytest.fixture
def spawns(monkeypatch):
    """Collect ``subprocess.Popen`` calls instead of launching a real capture."""
    calls: list = []

    def fake_popen(cmd, **kwargs):
        calls.append((cmd, kwargs))
        return object()

    monkeypatch.setattr(wrapper.subprocess, "Popen", fake_popen)
    # Keep the importability precondition out of these tests: it has its own
    # branch with its own message.
    monkeypatch.setattr(wrapper, "_codewiki_launch_env", lambda: (dict(os.environ), ""))
    return calls


def _invoke(monkeypatch, capsys, raw: bytes, *, tty: bool = False) -> dict:
    """Run the wrapper's main() with the given stdin and return its JSON payload."""
    monkeypatch.setattr("sys.stdin", _TtyStdin() if tty else _PipedStdin(raw))
    rc = wrapper.main()
    assert rc == 0  # the hook must never fail the IDE session
    out = capsys.readouterr().out
    assert out.count("\n") == 1, f"expected exactly one stdout line, got {out!r}"
    return json.loads(out)


# --------------------------------------------------------------------------- #
# 1. No usable event -> honest skip, no child spawned
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    ("raw", "reason_fragment"),
    [
        (b"", "no event on stdin"),
        # `\C` is not a valid JSON escape — the exact shape of a Windows cwd
        # pasted with backslashes on the command line.
        (b'{"cwd":"d:\\CodeWiki-Plus"}', "not valid JSON"),
        (b"not json at all", "not valid JSON"),
        (b"[]", "not an object"),
        (b"{}", "empty JSON object"),
    ],
)
def test_unusable_event_reports_skip_without_spawning(
    monkeypatch, capsys, spawns, raw, reason_fragment
):
    payload = _invoke(monkeypatch, capsys, raw)

    assert payload["continue"] is True
    assert payload["systemMessage"].startswith("team-memory capture skipped: ")
    assert reason_fragment in payload["systemMessage"]
    assert spawns == [], "a doomed child must not be launched"


def test_interactive_invocation_reports_skip(monkeypatch, capsys, spawns):
    payload = _invoke(monkeypatch, capsys, b"", tty=True)

    assert "skipped" in payload["systemMessage"]
    assert "interactively" in payload["systemMessage"]
    assert spawns == []


# --------------------------------------------------------------------------- #
# 2. Usable event -> forwarded to a detached child, fire-and-forget line
# --------------------------------------------------------------------------- #
def test_valid_event_is_forwarded_to_detached_child(monkeypatch, capsys, tmp_path, spawns):
    event_file = tmp_path / "event.json"

    def fake_mkstemp(**kwargs):
        assert kwargs.get("suffix") == ".json"
        return os.open(event_file, os.O_CREAT | os.O_TRUNC | os.O_WRONLY), str(event_file)

    monkeypatch.setattr(wrapper.tempfile, "mkstemp", fake_mkstemp)

    event = {
        "session_id": "sess-1",
        "transcript_path": "d:/tmp/conv.json",
        "cwd": str(tmp_path),
        "hook_event_name": "SessionEnd",
        "reason": "other",
    }
    payload = _invoke(monkeypatch, capsys, json.dumps(event).encode("utf-8"))

    assert payload == {
        "continue": True,
        "systemMessage": "team-memory capture started in background",
    }

    ((cmd, kwargs),) = spawns
    assert cmd[:3] == [sys.executable, "-m", "codewiki.mcp._ide_hook"]
    assert cmd[cmd.index("--enable")] == "--enable"
    # The event travels as a temp --conversation file; the child owns deleting it.
    assert cmd[cmd.index("--conversation") + 1] == str(event_file)
    assert json.loads(event_file.read_text(encoding="utf-8")) == event
    assert kwargs["env"]["CODEWIKI_HOOK_EVENT_FILE"] == str(event_file)
    # Detached: the IDE never waits, and the child's output never leaks into the
    # hook's stdout (which is the IDE's injection channel).
    assert kwargs["stdout"] is wrapper.subprocess.DEVNULL
    assert kwargs["stderr"] is wrapper.subprocess.DEVNULL


def test_utf8_bom_is_tolerated(monkeypatch, capsys, spawns):
    """PowerShell pipes may prepend a BOM; it must not become a skip."""
    event = {"session_id": "sess-bom", "hook_event_name": "SessionEnd"}
    payload = _invoke(monkeypatch, capsys, b"\xef\xbb\xbf" + json.dumps(event).encode("utf-8"))

    assert payload["systemMessage"] == "team-memory capture started in background"
    assert len(spawns) == 1
