"""Centralized task-memory limits (ADR-0013, borrowed from letta's
``directory-limits.ts`` pattern: all size limits in one module).

Scope (ADR-0013 decision 3): ONLY implementation constants from
``task_manager.py`` are collected here — the compaction threshold group and
the write-window soft limit. Retrieval token budgets and warm-layer injection
limits are deliberately NOT collected: they are behaviour-contract copy
(Agent-visible descriptions in registry.py / prompts.py), whose value lies in
the Agent seeing them, not in deduplication.

The registry/prompts copy that mirrors these numbers is guarded by the
``threshold_drift`` lint check (wiki_lint.py), NOT by f-string generation —
those descriptions are behaviour protocols read by the LLM, readability first.
"""

from __future__ import annotations

# Compaction thresholds and keep-window (see docs/任务记忆存储与加载扩展性
# 设计方案.md §3 Q6/Q7; ADR-0001). The compact tool is a stateless two-phase
# (prepare/submit) MCP tool — the LLM summary is produced by the CALLER, never
# by this tool (same constraint as distill_conversation's Mode C).
COMPACTION_THRESHOLD_COUNT = 40
COMPACTION_THRESHOLD_BYTES = 24 * 1024
COMPACTION_KEEP = 20
COMPACTION_SUMMARY_MAX_CHARS = 4096

# Write-window soft limit: number of add_task_memory writes per window before
# the tool starts hinting about compaction (soft — writes are never rejected).
WRITE_WINDOW_SOFT_LIMIT = 5

# ADR-0009 D9: compaction level — yellow/orange/red at 75%/87.5%/100% of the
# existing thresholds (count and bytes, whichever is worse).
COMPACTION_LEVEL_YELLOW = 0.75
COMPACTION_LEVEL_ORANGE = 0.875
