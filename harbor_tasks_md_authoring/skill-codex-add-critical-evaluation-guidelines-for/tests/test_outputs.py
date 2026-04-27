"""Behavioral checks for skill-codex-add-critical-evaluation-guidelines-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/skill-codex")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert 'echo "This is Claude (Opus 4.5) following up. I disagree with [X] because [evidence]. What\'s your take on this?" | codex exec --skip-git-repo-check resume --last 2>/dev/null' in text, "expected to find: " + 'echo "This is Claude (Opus 4.5) following up. I disagree with [X] because [evidence]. What\'s your take on this?" | codex exec --skip-git-repo-check resume --last 2>/dev/null'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '- **Trust your own knowledge** when confident. If Codex claims something you know is incorrect (e.g., "Claude Opus 4.5 doesn\'t exist"), push back directly.' in text, "expected to find: " + '- **Trust your own knowledge** when confident. If Codex claims something you know is incorrect (e.g., "Claude Opus 4.5 doesn\'t exist"), push back directly.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert "- **Research disagreements** using WebSearch or documentation before accepting Codex's claims. Share findings with Codex via resume if needed." in text, "expected to find: " + "- **Research disagreements** using WebSearch or documentation before accepting Codex's claims. Share findings with Codex via resume if needed."[:80]

