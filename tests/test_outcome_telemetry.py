# -*- coding: utf-8 -*-
"""Tests for outcome 采集（负反馈与经验通道，docs/负反馈与经验通道设计方案.md）.

Acceptance chain (design §八):
1. report_outcome writes the event: doc+task_id dual-anchor, optional note,
   adopted-key association copy
2. aggregate_usage returns per-doc success/failure counts
3. wiki_stats surfaces the outcome section (incl. outcome_ratio)
4. distill/consolidate prepare carry negative_examples (30-day window,
   cap 5, consistent with telemetry)
5. No frontmatter writes, no confirm gate, no behaviour change anywhere
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

from codewiki.mcp.session import SessionStore
from codewiki.mcp.tools import distill_conversation as distill
from codewiki.mcp.tools import note_consolidation as cons
from codewiki.mcp.tools.outcome_report import handle_report_outcome
from codewiki.mcp.tools.telemetry import (
    aggregate_usage,
    recent_outcome_failures,
    record_adopted,
    record_outcome,
)
from codewiki.mcp.tools.wiki_stats import _outcome_summary, handle_wiki_stats
from codewiki.src.config import RAW_DIR, user_id
from codewiki.src.store import KnowledgeStore


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _user_file(od: Path) -> Path:
    d = od / ".meta" / "telemetry"
    d.mkdir(parents=True, exist_ok=True)
    return d / f"{user_id()}.jsonl"


def _events(od: Path, user: str) -> list:
    p = od / ".meta" / "telemetry" / f"{user}.jsonl"
    if not p.exists():
        return []
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def _make_repo(tmp_path: Path) -> tuple:
    repo = tmp_path / "repo"
    od = repo / "repowiki"
    (od / "notes").mkdir(parents=True)
    (od / "notes" / "x.md").write_text(
        "---\ntype: pitfall\ntitle: 既有坑\nstatus: stable\n---\n\n正文\n",
        encoding="utf-8",
    )
    return repo, od


def _write_raw(repo: Path, cid: str, body: str = "user: hi\nassistant: hello") -> None:
    raw_dir = repo / "repowiki" / RAW_DIR
    raw_dir.mkdir(parents=True, exist_ok=True)
    (raw_dir / f"conv-{cid}.md").write_text(
        "---\n"
        "type: conversation\n"
        f'conversation_id: "{cid}"\n'
        "status: pending\n"
        "origin: conversation\n"
        "---\n\n" + body,
        encoding="utf-8",
    )


def _outcome(od: Path, args: dict) -> dict:
    store = SessionStore()
    return json.loads(handle_report_outcome({"repo_path": str(od.parent), **args}, store))


# --------------------------------------------------------------------------- #
# 1. report_outcome: event shape, dual anchor, adopted-key copy
# --------------------------------------------------------------------------- #
class TestReportOutcome:
    def test_minimal_event_shape(self, tmp_path):
        repo, od = _make_repo(tmp_path)
        r = _outcome(od, {"doc": "notes/x.md", "result": "success"})
        assert r["status"] == "recorded"
        evs = _events(od, user_id())
        assert len(evs) == 1
        ev = evs[0]
        assert ev["t"] == "outcome"
        assert ev["doc"] == "notes/x.md"
        assert ev["result"] == "success"
        # optional fields omitted when empty (minimal event = one clean line)
        assert "task_id" not in ev
        assert "note" not in ev
        assert "adopted_key" not in ev

    def test_dual_anchor_task_from_session_binding(self, tmp_path):
        repo, od = _make_repo(tmp_path)
        KnowledgeStore(od).write_binding("sess-1", "任务A")
        r = _outcome(
            od,
            {
                "doc": "notes/x.md",
                "result": "failure",
                "source_session_id": "sess-1",
                "note": "锁语义照抄反而死锁",
            },
        )
        assert r["task_id"] == "任务A"
        ev = _events(od, user_id())[0]
        assert ev["task_id"] == "任务A"
        assert ev["note"] == "锁语义照抄反而死锁"

    def test_explicit_task_id_wins(self, tmp_path):
        repo, od = _make_repo(tmp_path)
        KnowledgeStore(od).write_binding("sess-1", "任务A")
        r = _outcome(
            od,
            {
                "doc": "notes/x.md",
                "result": "success",
                "task_id": "显式任务",
                "source_session_id": "sess-1",
            },
        )
        assert r["task_id"] == "显式任务"

    def test_adopted_key_copy_same_session(self, tmp_path):
        repo, od = _make_repo(tmp_path)
        record_adopted(od, "notes/x.md", f"{user_id()}/sess-1")
        r = _outcome(
            od,
            {"doc": "notes/x.md", "result": "success", "source_session_id": "sess-1"},
        )
        assert r["adopted_key"] == f"{user_id()}/sess-1"
        ev = _events(od, user_id())[-1]  # adopted line first, outcome appended
        assert ev["t"] == "outcome"
        assert ev["adopted_key"] == f"{user_id()}/sess-1"

    def test_adopted_key_copy_via_task_lineage(self, tmp_path):
        # explicit task_id only: reverse-lookup the task's sessions, copy
        # an adoption recorded under one of them
        repo, od = _make_repo(tmp_path)
        ks = KnowledgeStore(od)
        ks.write_binding("sess-2", "任务A")
        record_adopted(od, "notes/x.md", f"{user_id()}/sess-2")
        r = _outcome(od, {"doc": "notes/x.md", "result": "success", "task_id": "任务A"})
        assert r["adopted_key"] == f"{user_id()}/sess-2"

    def test_adopted_key_not_copied_from_other_task(self, tmp_path):
        repo, od = _make_repo(tmp_path)
        ks = KnowledgeStore(od)
        ks.write_binding("sess-other", "别的任务")
        record_adopted(od, "notes/x.md", f"{user_id()}/sess-other")
        r = _outcome(od, {"doc": "notes/x.md", "result": "success", "task_id": "任务A"})
        assert "adopted_key" not in r

    def test_validation(self, tmp_path):
        repo, od = _make_repo(tmp_path)
        # bad result (binary only — no grading)
        r = _outcome(od, {"doc": "notes/x.md", "result": "partial"})
        assert "error" in r
        # missing doc
        r = _outcome(od, {"result": "success"})
        assert "error" in r
        # doc must exist under the wiki
        r = _outcome(od, {"doc": "notes/ghost.md", "result": "success"})
        assert "error" in r
        # path normalisation: backslashes / ./ prefix accepted
        r = _outcome(od, {"doc": r".\notes\x.md", "result": "success"})
        assert r["status"] == "recorded"
        assert r["doc"] == "notes/x.md"


# --------------------------------------------------------------------------- #
# 2. aggregate_usage: per-doc success/failure counts
# --------------------------------------------------------------------------- #
class TestAggregateOutcome:
    def test_counts_and_invalid_result_skipped(self, tmp_path):
        repo, od = _make_repo(tmp_path)
        record_outcome(od, "notes/x.md", "success")
        record_outcome(od, "notes/x.md", "success")
        record_outcome(od, "notes/x.md", "failure")
        record_outcome(od, "notes/x.md", "partial")  # invalid → neither counter
        agg = aggregate_usage(od)
        e = agg["notes/x.md"]
        assert e["success"] == 2
        assert e["failure"] == 1

    def test_by_file_pipe_stays_separate(self, tmp_path):
        repo, od = _make_repo(tmp_path)
        record_outcome(od, "notes/x.md", "success")
        agg = aggregate_usage(od)
        assert agg["notes/x.md"]["hits"] == 0


# --------------------------------------------------------------------------- #
# 3. wiki_stats outcome section
# --------------------------------------------------------------------------- #
class TestWikiStatsOutcome:
    def test_summary_ratio(self):
        usage = {
            "notes/a.md": {"success": 3, "failure": 1},
            "notes/b.md": {"success": 0, "failure": 1},
        }
        s = _outcome_summary(usage)
        assert s == {"success": 3, "failure": 2, "outcome_ratio": 0.6}

    def test_summary_none_without_events(self):
        assert _outcome_summary({}) is None
        assert _outcome_summary({"notes/a.md": {"success": 0, "failure": 0}}) is None

    def test_handler_surfaces_outcome_section(self, tmp_path):
        repo, od = _make_repo(tmp_path)
        record_outcome(od, "notes/x.md", "success", task_id="任务A")
        record_outcome(od, "notes/x.md", "failure")
        store = SessionStore()
        out = json.loads(handle_wiki_stats({"repo_path": str(repo)}, store))
        # outcome events alone make usage non-empty → main path, not early return
        assert "outcome" in out
        assert out["outcome"]["success"] == 1
        assert out["outcome"]["failure"] == 1
        assert out["outcome"]["outcome_ratio"] == 0.5

    def test_handler_no_section_without_events(self, tmp_path):
        repo, od = _make_repo(tmp_path)
        store = SessionStore()
        out = json.loads(handle_wiki_stats({"repo_path": str(repo)}, store))
        assert "outcome" not in out


# --------------------------------------------------------------------------- #
# 4. negative_examples: window, cap, prepare wiring
# --------------------------------------------------------------------------- #
class TestRecentOutcomeFailures:
    def _write_event(self, od: Path, doc: str, result: str, days_ago: int, note: str = ""):
        at = (datetime.now() - timedelta(days=days_ago)).isoformat(timespec="seconds")
        ev = {"t": "outcome", "doc": doc, "at": at, "result": result}
        if note:
            ev["note"] = note
        p = _user_file(od)
        with open(p, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(ev, ensure_ascii=False) + "\n")

    def test_window_and_filtering(self, tmp_path):
        repo, od = _make_repo(tmp_path)
        self._write_event(od, "notes/a.md", "failure", 5, note="用法甲错了")
        self._write_event(od, "notes/a.md", "failure", 40)  # outside 30d window
        self._write_event(od, "notes/b.md", "success", 1)  # successes excluded
        rows = recent_outcome_failures(od)
        assert len(rows) == 1
        assert rows[0]["doc"] == "notes/a.md"
        assert rows[0]["note"] == "用法甲错了"

    def test_cap_and_newest_first(self, tmp_path):
        repo, od = _make_repo(tmp_path)
        for i in range(7):
            self._write_event(od, f"notes/n{i}.md", "failure", days_ago=10 - i)
        rows = recent_outcome_failures(od)
        assert len(rows) == 5
        assert [r["doc"] for r in rows] == [f"notes/n{i}.md" for i in (6, 5, 4, 3, 2)]


class TestNegativeExamplesInPrepare:
    def test_distill_prepare_carries_negative_examples(self, tmp_path):
        repo, od = _make_repo(tmp_path)
        _write_raw(repo, "neg-1")
        record_outcome(od, "notes/x.md", "failure", task_id="任务A", note="照抄锁语义导致死锁")
        store = SessionStore()
        out = json.loads(
            distill.handle_distill_conversation({"repo_path": str(repo), "mode": "prepare"}, store)
        )
        assert out["status"] == "prepared"
        assert out["negative_examples"] == [
            {"doc": "notes/x.md", "note": "照抄锁语义导致死锁", "task_id": "任务A"}
        ]
        assert "规避同模式" in out["negative_examples_hint"]

    def test_distill_prepare_no_section_without_failures(self, tmp_path):
        repo, od = _make_repo(tmp_path)
        _write_raw(repo, "neg-2")
        record_outcome(od, "notes/x.md", "success")
        store = SessionStore()
        out = json.loads(
            distill.handle_distill_conversation({"repo_path": str(repo), "mode": "prepare"}, store)
        )
        assert "negative_examples" not in out

    def test_consolidate_prepare_carries_negative_examples(self, tmp_path):
        repo, od = _make_repo(tmp_path)
        record_outcome(od, "notes/x.md", "failure", note="归因错了一层")
        store = SessionStore()
        out = json.loads(
            cons.handle_consolidate_notes({"repo_path": str(repo), "mode": "prepare"}, store)
        )
        assert out["status"] == "prepared"
        assert out["negative_examples"][0]["doc"] == "notes/x.md"
        assert "规避同模式" in out["negative_examples_hint"]

    def test_consolidate_prepare_no_section_without_failures(self, tmp_path):
        repo, od = _make_repo(tmp_path)
        store = SessionStore()
        out = json.loads(
            cons.handle_consolidate_notes({"repo_path": str(repo), "mode": "prepare"}, store)
        )
        assert "negative_examples" not in out


# --------------------------------------------------------------------------- #
# 5. no side effects: telemetry events never touch frontmatter
# --------------------------------------------------------------------------- #
def test_outcome_never_touches_frontmatter(tmp_path):
    repo, od = _make_repo(tmp_path)
    before = (od / "notes" / "x.md").read_text(encoding="utf-8")
    _outcome(od, {"doc": "notes/x.md", "result": "failure", "task_id": "任务A"})
    after = (od / "notes" / "x.md").read_text(encoding="utf-8")
    assert before == after
