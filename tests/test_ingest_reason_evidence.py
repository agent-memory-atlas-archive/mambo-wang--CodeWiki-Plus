"""ADR-0013 (letta borrow, 方案 B): ingest_note reason/evidence semantics.

- status='stable' direct-write bypasses the draft→confirm gate → reason
  REQUIRED (intent declaration; visibility/friction/attribution — NOT a
  verification mechanism).
- Optional evidence (test_ref/commit_ref/reviewed_by) mirrors confirm_note:
  promotes confidence_level to strong, records metadata.verification,
  rejects unknown keys.
- draft is exempt (confirm gate downstream).
"""

from __future__ import annotations

import json
from pathlib import Path

from codewiki.mcp.session import SessionStore
from codewiki.mcp.tools import note_ingest as ni
from codewiki.src.frontmatter import parse_frontmatter


class _Store(SessionStore):
    pass


def _call(fn, **kw) -> dict:
    return json.loads(fn(kw, _Store()))


def _ingest(repo: Path, title: str, content: str = "测试正文内容。", **extra) -> dict:
    args = {"repo_path": str(repo), "title": title, "content": content, "note_type": "general"}
    args.update(extra)
    return _call(ni.handle_ingest_note, **args)


def _note_name(r: dict) -> str:
    return Path(r["note_path"]).name


def _fm_of(repo: Path, rel: str) -> dict:
    fm, body = parse_frontmatter((repo / "repowiki" / rel).read_text(encoding="utf-8"))
    return fm


def test_stable_without_reason_rejected(tmp_path):
    r = _ingest(tmp_path, "无理由直写", status="stable")
    assert "error" in r
    assert "reason is required" in r["error"]
    # nothing written
    assert not list((tmp_path / "repowiki" / "notes").glob("*.md"))


def test_stable_with_reason_accepted_and_stamped(tmp_path):
    r = _ingest(tmp_path, "有理由直写", status="stable", reason="用户本会话明确拍板")
    assert r["status"] == "ingested"
    fm = _fm_of(tmp_path, f"notes/{_note_name(r)}")
    meta = fm.get("metadata") or {}
    assert fm["status"] == "stable"
    assert meta.get("reason") == "用户本会话明确拍板"


def test_draft_reason_optional(tmp_path):
    # draft without reason: fine (confirm gate downstream)
    r = _ingest(tmp_path, "草稿无理由")
    assert r["status"] == "ingested"
    # draft with reason: also fine, stamped for audit
    r2 = _ingest(tmp_path, "草稿带理由", reason="蒸馏产物，rationale 见正文")
    assert r2["status"] == "ingested"
    fm = _fm_of(tmp_path, f"notes/{_note_name(r2)}")
    meta = fm.get("metadata") or {}
    assert meta.get("reason") == "蒸馏产物，rationale 见正文"


def test_evidence_promotes_strong_and_records_verification(tmp_path):
    r = _ingest(
        tmp_path,
        "带证据直写",
        status="stable",
        reason="迁移已验证知识",
        evidence={"test_ref": "tests/test_threshold_drift.py", "commit_ref": "abc1234"},
    )
    assert r["status"] == "ingested"
    fm = _fm_of(tmp_path, f"notes/{_note_name(r)}")
    meta = fm.get("metadata") or {}
    assert fm["status"] == "stable"
    assert meta.get("confidence_level") == "strong"
    assert meta.get("verification") == {
        "test_ref": "tests/test_threshold_drift.py",
        "commit_ref": "abc1234",
    }


def test_evidence_unknown_keys_rejected(tmp_path):
    r = _ingest(
        tmp_path,
        "伪证据直写",
        status="stable",
        reason="x",
        evidence={"foo": "bar"},
    )
    assert "error" in r
    assert "unknown key" in r["error"]


def test_evidence_non_object_rejected(tmp_path):
    r = _ingest(tmp_path, "字符串证据", status="stable", reason="x", evidence="tests/foo.py")
    assert "error" in r
    assert "evidence must be an object" in r["error"]


def test_evidence_without_still_allowed_on_draft(tmp_path):
    # evidence on a draft is legal (pre-verified knowledge ingested as draft
    # for the confirm gate) — strong confidence carries over
    r = _ingest(tmp_path, "带证据草稿", evidence={"reviewed_by": "human:wangbao"})
    assert r["status"] == "ingested"
    fm = _fm_of(tmp_path, f"notes/{_note_name(r)}")
    meta = fm.get("metadata") or {}
    assert meta.get("confidence_level") == "strong"
    assert meta.get("verification") == {"reviewed_by": "human:wangbao"}
