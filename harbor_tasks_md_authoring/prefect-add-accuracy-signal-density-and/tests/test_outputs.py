"""Behavioral checks for prefect-add-accuracy-signal-density-and (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/prefect")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/agents-md-sync/SKILL.md')
    assert "- Don't suggest adding content that's obvious from the code itself. AGENTS.md captures non-obvious patterns, gotchas, and high-level structure. Equally, flag *existing* content that merely restates th" in text, "expected to find: " + "- Don't suggest adding content that's obvious from the code itself. AGENTS.md captures non-obvious patterns, gotchas, and high-level structure. Equally, flag *existing* content that merely restates th"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/agents-md-sync/SKILL.md')
    assert '- Look for undocumented invariants — parallel implementations that must stay in sync, ordering constraints, singleton behaviors, cleanup responsibilities. These are the highest-value additions because' in text, "expected to find: " + '- Look for undocumented invariants — parallel implementations that must stay in sync, ordering constraints, singleton behaviors, cleanup responsibilities. These are the highest-value additions because'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/agents-md-sync/SKILL.md')
    assert "For claims that are verifiable (specific behaviors, function signatures, which module does what), read the source file and confirm. Don't trust that existing AGENTS.md content was ever correct — it ma" in text, "expected to find: " + "For claims that are verifiable (specific behaviors, function signatures, which module does what), read the source file and confirm. Don't trust that existing AGENTS.md content was ever correct — it ma"[:80]

