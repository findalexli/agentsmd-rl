"""Behavioral checks for everything-claude-code-featskills-add-teambuilder-skill (markdown_authoring task).

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
    text = _read('skills/team-builder/SKILL.md')
    assert '- **Flat layout:** collect all filename prefixes (text before the first `-`). A prefix qualifies as a domain only if it appears in 2 or more filenames (e.g., `engineering-security-engineer.md` and `en' in text, "expected to find: " + '- **Flat layout:** collect all filename prefixes (text before the first `-`). A prefix qualifies as a domain only if it appears in 2 or more filenames (e.g., `engineering-security-engineer.md` and `en'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/team-builder/SKILL.md')
    assert '**Flat layout** — domain inferred from shared filename prefixes. A prefix counts as a domain when 2+ files share it. Files with unique prefixes go to "General". Note: the algorithm splits at the first' in text, "expected to find: " + '**Flat layout** — domain inferred from shared filename prefixes. A prefix counts as a domain when 2+ files share it. Files with unique prefixes go to "General". Note: the algorithm splits at the first'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/team-builder/SKILL.md')
    assert '- **Parallel Agent calls, not TeamCreate.** This skill uses parallel Agent tool calls for independent work. TeamCreate (a Claude Code tool for multi-agent dialogue) is only needed when agents must deb' in text, "expected to find: " + '- **Parallel Agent calls, not TeamCreate.** This skill uses parallel Agent tool calls for independent work. TeamCreate (a Claude Code tool for multi-agent dialogue) is only needed when agents must deb'[:80]

