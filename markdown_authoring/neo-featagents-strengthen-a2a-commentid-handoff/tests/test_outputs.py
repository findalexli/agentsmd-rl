"""Behavioral checks for neo-featagents-strengthen-a2a-commentid-handoff (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/neo")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/pr-review/references/pr-review-guide.md')
    assert '**Problem:** Without commentId-scoped fetch, every review cycle N+1 incurs **cumulative-thread context cost** — full-thread fetch reads all prior cycles, not just the delta. This breaks linear-cost sc' in text, "expected to find: " + '**Problem:** Without commentId-scoped fetch, every review cycle N+1 incurs **cumulative-thread context cost** — full-thread fetch reads all prior cycles, not just the delta. This breaks linear-cost sc'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/pr-review/references/pr-review-guide.md')
    assert 'The dichotomy mirrors the boot-pull-vs-sunset-pull lifecycle distinction (`AGENTS_STARTUP §0` vs `session-sunset` skill body Step 1): **warm path** optimizes for incremental context; **cold path** gro' in text, "expected to find: " + 'The dichotomy mirrors the boot-pull-vs-sunset-pull lifecycle distinction (`AGENTS_STARTUP §0` vs `session-sunset` skill body Step 1): **warm path** optimizes for incremental context; **cold path** gro'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/pr-review/references/pr-review-guide.md')
    assert '**Empirical anchor (PR #10371, 2026-04-26):** Cycle 3 thread reached ~8KB markdown across 6 prior comments. Full-thread fetch by Cycle 4 reviewer reads all 8KB to extract the ~1KB delta from one new c' in text, "expected to find: " + '**Empirical anchor (PR #10371, 2026-04-26):** Cycle 3 thread reached ~8KB markdown across 6 prior comments. Full-thread fetch by Cycle 4 reviewer reads all 8KB to extract the ~1KB delta from one new c'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/pull-request/references/pull-request-workflow.md')
    assert '**Pre-Flight Check (operational reflex)** — mirrors `AGENTS.md §3 / §4.2` proven primitive. After every author-side `manage_issue_comment` create, before yielding turn, explicitly state in your reason' in text, "expected to find: " + '**Pre-Flight Check (operational reflex)** — mirrors `AGENTS.md §3 / §4.2` proven primitive. After every author-side `manage_issue_comment` create, before yielding turn, explicitly state in your reason'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/pull-request/references/pull-request-workflow.md')
    assert '**Cold-cache exception:** When picking up a PR after a fresh session bootstrap, opening Cycle 1 of a PR, taking a cross-agent handoff, or recovering from a missed/lost reviewer ping, full-thread fetch' in text, "expected to find: " + '**Cold-cache exception:** When picking up a PR after a fresh session bootstrap, opening Cycle 1 of a PR, taking a cross-agent handoff, or recovering from a missed/lost reviewer ping, full-thread fetch'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "| `pr-review` | Reviewing a PR (yours or peer's) — structured eval metrics, graph ingestion tags, severity ladder, restates §0 merge gate, post-comment A2A commentId hand-off (reviewer→author) per gui" in text, "expected to find: " + "| `pr-review` | Reviewing a PR (yours or peer's) — structured eval metrics, graph ingestion tags, severity ladder, restates §0 merge gate, post-comment A2A commentId hand-off (reviewer→author) per gui"[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '| `pull-request` | Code modifications complete; before opening PR — stepping-back reflection, commit format, cross-family review mandate, post-comment A2A commentId hand-off (author→reviewer) per work' in text, "expected to find: " + '| `pull-request` | Code modifications complete; before opening PR — stepping-back reflection, commit format, cross-family review mandate, post-comment A2A commentId hand-off (author→reviewer) per work'[:80]

