"""Phase5 T1: backfill confidence_level onto existing repowiki assets.

Idempotent one-shot migration. Mapping (design docs/Phase5-资产治理-实现任务拆解.md T1):

- notes/        stable -> weak,  draft -> weak,  deprecated -> shadow
- scenarios/    (L2 scene blocks) -> weak (agent-authored, verified-on-confirm)
- doctrine.md   strong (stable-premise top layer — doctrine refresh already
                requires human confirmation)

An asset that already carries metadata.confidence_level is left untouched
(idempotency). Only the metadata fold is written; status and every other
frontmatter key round-trip unchanged.

Usage:
    uv run python scripts/migrate_confidence.py <repo_path> [--dry-run]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running from a source checkout without installation.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from codewiki.src.config import NOTES_DIR, WIKI_DIR  # noqa: E402
from codewiki.src.frontmatter import parse_frontmatter  # noqa: E402


def _confidence_for_note(status: str) -> str:
    s = (status or "").strip().lower()
    if s == "deprecated":
        return "shadow"  # rejected/superseded assets leave the trusted pool
    # stable → weak (confirmed but unverified); draft → weak too — a draft is
    # still visible with its [unconfirmed] prefix, shadow is reserved for
    # rejected/misrecalled assets (not drafts).
    return "weak"


def _migrate_file(path: Path, level: str, dry_run: bool) -> str:
    """Return one of: skipped | migrated | error:<msg>."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        return f"error:{e}"
    fm, body = parse_frontmatter(text)
    if not fm:
        return "skipped"  # no readable frontmatter — leave for lint to flag
    meta = fm.get("metadata") if isinstance(fm.get("metadata"), dict) else {}
    if meta.get("confidence_level"):
        return "skipped"  # already migrated (idempotency)
    fm = dict(fm)
    meta = dict(meta)
    meta["confidence_level"] = level
    fm["metadata"] = meta

    import yaml

    from codewiki.src.store import atomic_write, locked

    new_text = f"---\n{yaml.safe_dump(fm, allow_unicode=True, sort_keys=False)}---\n{body}"
    if not dry_run:
        with locked(path):
            atomic_write(path, new_text)
    return "migrated"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("repo_path", help="Repository root (repowiki lives at <repo>/repowiki)")
    ap.add_argument("--dry-run", action="store_true", help="Report without writing")
    args = ap.parse_args()

    repo = Path(args.repo_path).expanduser().resolve()
    od = repo / "repowiki"
    if not od.is_dir():
        print(f"error: {od} does not exist", file=sys.stderr)
        return 1

    counts = {"migrated": 0, "skipped": 0, "errors": 0}

    def _run(label: str, paths, level_for):
        for p in sorted(paths):
            level = level_for(p)
            if level is None:
                continue
            r = _migrate_file(p, level, args.dry_run)
            if r.startswith("error:"):
                counts["errors"] += 1
                print(f"  [{label}] ERROR {p.name}: {r[6:]}")
            else:
                counts[r] += 1

    # notes/ — level derived from status
    notes_dir = od / NOTES_DIR
    if notes_dir.is_dir():

        def _note_level(p: Path):
            fm, _ = parse_frontmatter(p.read_text(encoding="utf-8", errors="replace"))
            if not fm:
                return None
            return _confidence_for_note(str(fm.get("status") or "draft"))

        _run("notes", notes_dir.glob("*.md"), _note_level)

    # scenarios/ — always weak
    scen_dir = od / WIKI_DIR / "scenarios"
    if scen_dir.is_dir():
        _run("scenarios", scen_dir.glob("*.md"), lambda p: "weak")

    # doctrine.md — strong
    doctrine = od / WIKI_DIR / "doctrine.md"
    if doctrine.is_file():
        _run("doctrine", [doctrine], lambda p: "strong")

    suffix = " (dry-run)" if args.dry_run else ""
    print(
        f"confidence migration{suffix}: migrated={counts['migrated']} "
        f"skipped(already/none)={counts['skipped']} errors={counts['errors']}"
    )
    return 0 if counts["errors"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
