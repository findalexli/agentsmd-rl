"""Behavioral checks for sanity-choreskills-update-prdescription-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/sanity")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/pr-description/SKILL.md')
    assert '**Length test:** if a sentence would tell the reviewer something they could deduce in 10 seconds from the diff, cut it. A good PR description is often 3–5 sentences total. Bulleted lists of "alternati' in text, "expected to find: " + '**Length test:** if a sentence would tell the reviewer something they could deduce in 10 seconds from the diff, cut it. A good PR description is often 3–5 sentences total. Bulleted lists of "alternati'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/pr-description/SKILL.md')
    assert "- **Cover _why not_** — alternatives considered and rejected, one sentence each. This is often the most valuable part: it prevents the reviewer from suggesting a path you've already ruled out. Skip if" in text, "expected to find: " + "- **Cover _why not_** — alternatives considered and rejected, one sentence each. This is often the most valuable part: it prevents the reviewer from suggesting a path you've already ruled out. Skip if"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/pr-description/SKILL.md')
    assert 'If you catch yourself writing "this PR renames X to Y" or "adds a new function Z", delete it. If you\'re explaining _why_ X needed to be renamed or _why_ Z exists (and why the obvious alternative wasn\'' in text, "expected to find: " + 'If you catch yourself writing "this PR renames X to Y" or "adds a new function Z", delete it. If you\'re explaining _why_ X needed to be renamed or _why_ Z exists (and why the obvious alternative wasn\''[:80]

