"""Behavioral checks for lobehub-docsskills-record-contributor-roster-in (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/lobehub")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/version-release/SKILL.md')
    assert 'Render contributors as a **single flat list** (no separate "Community" / "Core Team" subsections). Order: **community contributors first, team members after**. Within each group, sort by PR count desc' in text, "expected to find: " + 'Render contributors as a **single flat list** (no separate "Community" / "Core Team" subsections). Order: **community contributors first, team members after**. Within each group, sort by PR count desc'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/version-release/SKILL.md')
    assert "> **Resolving handles** — git author names (e.g. `YuTengjing`) are not always the GitHub handle. Verify via `gh pr view <PR> --json author` or `gh api search/users -f q='<email>'` before listing." in text, "expected to find: " + "> **Resolving handles** — git author names (e.g. `YuTengjing`) are not always the GitHub handle. Verify via `gh pr view <PR> --json author` or `gh api search/users -f q='<email>'` before listing."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/version-release/SKILL.md')
    assert 'If a new contributor appears who is not on this list, treat them as community by default and ask the user whether to add them to the roster.' in text, "expected to find: " + 'If a new contributor appears who is not on this list, treat them as community by default and ask the user whether to add them to the roster.'[:80]

