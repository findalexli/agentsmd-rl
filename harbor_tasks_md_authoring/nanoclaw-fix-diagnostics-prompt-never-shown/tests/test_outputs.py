"""Behavioral checks for nanoclaw-fix-diagnostics-prompt-never-shown (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nanoclaw")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup/SKILL.md')
    assert 'Send diagnostics data by following `.claude/skills/setup/diagnostics.md`.' in text, "expected to find: " + 'Send diagnostics data by following `.claude/skills/setup/diagnostics.md`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup/SKILL.md')
    assert '## 9. Diagnostics' in text, "expected to find: " + '## 9. Diagnostics'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup/diagnostics.md')
    assert '3. Remove the `## 9. Diagnostics` section from `.claude/skills/setup/SKILL.md` and the `## Diagnostics` section from `.claude/skills/update-nanoclaw/SKILL.md`' in text, "expected to find: " + '3. Remove the `## 9. Diagnostics` section from `.claude/skills/setup/SKILL.md` and the `## Diagnostics` section from `.claude/skills/update-nanoclaw/SKILL.md`'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/update-nanoclaw/SKILL.md')
    assert 'Send diagnostics data by following `.claude/skills/update-nanoclaw/diagnostics.md`.' in text, "expected to find: " + 'Send diagnostics data by following `.claude/skills/update-nanoclaw/diagnostics.md`.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/update-nanoclaw/diagnostics.md')
    assert '3. Remove the `## 9. Diagnostics` section from `.claude/skills/setup/SKILL.md` and the `## Diagnostics` section from `.claude/skills/update-nanoclaw/SKILL.md`' in text, "expected to find: " + '3. Remove the `## 9. Diagnostics` section from `.claude/skills/setup/SKILL.md` and the `## Diagnostics` section from `.claude/skills/update-nanoclaw/SKILL.md`'[:80]

