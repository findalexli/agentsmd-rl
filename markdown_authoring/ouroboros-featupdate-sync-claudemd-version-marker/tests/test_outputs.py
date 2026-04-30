"""Behavioral checks for ouroboros-featupdate-sync-claudemd-version-marker (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ouroboros")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/update/SKILL.md')
    assert 'sed -i.bak "s/<!-- ooo:VERSION:.*-->/<!-- ooo:VERSION:$NEW_VERSION -->/" CLAUDE.md && rm -f CLAUDE.md.bak' in text, "expected to find: " + 'sed -i.bak "s/<!-- ooo:VERSION:.*-->/<!-- ooo:VERSION:$NEW_VERSION -->/" CLAUDE.md && rm -f CLAUDE.md.bak'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/update/SKILL.md')
    assert 'OLD_VERSION=$(grep "ooo:VERSION" CLAUDE.md | sed \'s/.*ooo:VERSION:\\(.*\\) -->/\\1/\' | tr -d \' \')' in text, "expected to find: " + 'OLD_VERSION=$(grep "ooo:VERSION" CLAUDE.md | sed \'s/.*ooo:VERSION:\\(.*\\) -->/\\1/\' | tr -d \' \')'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/update/SKILL.md')
    assert 'NEW_VERSION=$(python3 -c "import ouroboros; print(ouroboros.__version__)" 2>/dev/null)' in text, "expected to find: " + 'NEW_VERSION=$(python3 -c "import ouroboros; print(ouroboros.__version__)" 2>/dev/null)'[:80]

