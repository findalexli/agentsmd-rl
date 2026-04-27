"""Behavioral checks for vitess-add-resolvebackport-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/vitess")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/resolve-backport/SKILL.md')
    assert "- **Missing dependencies**: If the conflicts exist because the upstream PR depends on changes from another PR that hasn't been backported yet, or if backporting an additional PR would make the resolut" in text, "expected to find: " + "- **Missing dependencies**: If the conflicts exist because the upstream PR depends on changes from another PR that hasn't been backported yet, or if backporting an additional PR would make the resolut"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/resolve-backport/SKILL.md')
    assert "- **File addition mismatch**: Check if any file that was a *modification* in the upstream PR appears as a *new file addition* on the backport branch (i.e., the file doesn't exist on the base release b" in text, "expected to find: " + "- **File addition mismatch**: Check if any file that was a *modification* in the upstream PR appears as a *new file addition* on the backport branch (i.e., the file doesn't exist on the base release b"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/resolve-backport/SKILL.md')
    assert '- Add a PR comment summarizing the conflict resolution. Include which files had conflicts, how they were resolved, and any notable decisions (e.g., keeping functions from prior backports, adapting cod' in text, "expected to find: " + '- Add a PR comment summarizing the conflict resolution. Include which files had conflicts, how they were resolved, and any notable decisions (e.g., keeping functions from prior backports, adapting cod'[:80]

