"""Behavioral checks for libretto-rename-libretto-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/libretto")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/libretto/SKILL.md')
    assert 'name: libretto' in text, "expected to find: " + 'name: libretto'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/push/SKILL.md')
    assert '2. If GitHub returns `no checks reported`, treat it as possible propagation delay. Wait 15 seconds and retry `gh pr checks --watch`. Repeat up to 8 times (about 2 minutes total) before concluding ther' in text, "expected to find: " + '2. If GitHub returns `no checks reported`, treat it as possible propagation delay. Wait 15 seconds and retry `gh pr checks --watch`. Repeat up to 8 times (about 2 minutes total) before concluding ther'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/push/SKILL.md')
    assert '4. If any test or type-check command fails, inspect logs immediately, fix the issue, commit, push, and repeat this CI loop until checks pass.' in text, "expected to find: " + '4. If any test or type-check command fails, inspect logs immediately, fix the issue, commit, push, and repeat this CI loop until checks pass.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/push/SKILL.md')
    assert '5. If checks are blocked on AI review bots, wait for bot completion and read all bot reviews before reporting completion.' in text, "expected to find: " + '5. If checks are blocked on AI review bots, wait for bot completion and read all bot reviews before reporting completion.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/libretto/skill/SKILL.md')
    assert 'name: libretto' in text, "expected to find: " + 'name: libretto'[:80]

