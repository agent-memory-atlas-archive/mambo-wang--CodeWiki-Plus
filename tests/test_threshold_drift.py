"""ADR-0013 threshold_drift lint check tests.

The check guards the behaviour-contract copy in registry.py / prompts.py
against drift from the single-source constants in
``codewiki/mcp/tools/limits.py``.  Copy is deliberately NOT f-string
generated (LLM-facing protocol text, readability first) — this lint is the
drift backstop.
"""

from __future__ import annotations

import importlib
from pathlib import Path

from codewiki.mcp.tools import limits
from codewiki.mcp.tools.wiki_lint import _ALL_CHECKS, _check_threshold_drift


def _issues():
    return _check_threshold_drift(Path("."))


def test_check_registered_in_all_checks():
    assert "threshold_drift" in _ALL_CHECKS


def test_registry_enum_contains_threshold_drift():
    from codewiki.mcp.registry import REGISTRY

    tool = REGISTRY["lint_wiki"]
    enum = tool.schema.inputSchema["properties"]["checks"]["items"]["enum"]
    assert "threshold_drift" in enum

    module_path, _, func_name = tool.handler_path.partition(":")
    module = importlib.import_module(module_path)
    assert callable(getattr(module, func_name))


def test_baseline_copy_matches_constants():
    """Current source copy must agree with limits.py (regression for the
    2048→4096 summary-chars drift the check caught on day one)."""
    assert _issues() == []


def test_drift_detected_when_constant_changes(monkeypatch):
    """Monkeypatching a constant must surface a warning pointing at the
    drifted copy file and line."""
    monkeypatch.setattr(limits, "COMPACTION_THRESHOLD_COUNT", 35)
    issues = _issues()
    assert issues, "drifted count constant must be reported"
    assert all(i["check"] == "threshold_drift" for i in issues)
    assert all(i["severity"] == "warning" for i in issues)
    count_issues = [i for i in issues if "threshold count" in i["message"]]
    assert count_issues, "the count drift must be among the reported issues"
    assert "registry.py" in count_issues[0]["file"]
    assert count_issues[0]["line"] > 0


def test_kb_drift_detected(monkeypatch):
    monkeypatch.setattr(limits, "COMPACTION_THRESHOLD_BYTES", 32 * 1024)
    issues = _issues()
    kb_issues = [i for i in issues if "threshold KB" in i["message"]]
    assert kb_issues, "the KB drift must be reported"


def test_unrelated_kb_numbers_not_flagged():
    """The >50KB large-file note in registry.py is NOT a compaction
    threshold — the anchored regex must not flag it."""
    text = (Path(limits.__file__).resolve().parent.parent / "registry.py").read_text(
        encoding="utf-8", errors="replace"
    )
    assert "50KB" in text  # the copy exists …
    baseline = _issues()
    assert not any("50" in i["message"] for i in baseline)  # … and is not flagged
