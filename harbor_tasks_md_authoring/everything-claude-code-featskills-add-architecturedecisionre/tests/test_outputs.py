"""Behavioral checks for everything-claude-code-featskills-add-architecturedecisionre (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/everything-claude-code")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/architecture-decision-records/SKILL.md')
    assert '1. **Initialize (first time only)** — if `docs/adr/` does not exist, ask the user for confirmation before creating the directory, a `README.md` seeded with the index table header (see ADR Index Format' in text, "expected to find: " + '1. **Initialize (first time only)** — if `docs/adr/` does not exist, ask the user for confirmation before creating the directory, a `README.md` seeded with the index table header (see ADR Index Format'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/architecture-decision-records/SKILL.md')
    assert 'description: Capture architectural decisions made during Claude Code sessions as structured ADRs. Auto-detects decision moments, records context, alternatives considered, and rationale. Maintains an A' in text, "expected to find: " + 'description: Capture architectural decisions made during Claude Code sessions as structured ADRs. Auto-detects decision moments, records context, alternatives considered, and rationale. Maintains an A'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/architecture-decision-records/SKILL.md')
    assert "Capture architectural decisions as they happen during coding sessions. Instead of decisions living only in Slack threads, PR comments, or someone's memory, this skill produces structured ADR documents" in text, "expected to find: " + "Capture architectural decisions as they happen during coding sessions. Instead of decisions living only in Slack threads, PR comments, or someone's memory, this skill produces structured ADR documents"[:80]

