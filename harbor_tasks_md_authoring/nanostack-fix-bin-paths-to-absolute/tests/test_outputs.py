"""Behavioral checks for nanostack-fix-bin-paths-to-absolute (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nanostack")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert "All skills reference scripts as `bin/save-artifact.sh`, `bin/find-artifact.sh`, etc. These paths are **relative to the nanostack skill root**, not to the user's project directory." in text, "expected to find: " + "All skills reference scripts as `bin/save-artifact.sh`, `bin/find-artifact.sh`, etc. These paths are **relative to the nanostack skill root**, not to the user's project directory."[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert 'If the nanostack root cannot be found, skip the script call and proceed with the skill. Never fail a skill because a helper script is missing.' in text, "expected to find: " + 'If the nanostack root cannot be found, skip the script call and proceed with the skill. Never fail a skill because a helper script is missing.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '[ ! -d "$NANOSTACK_ROOT" ] && NANOSTACK_ROOT="$(find "$HOME/.claude" -name "nanostack" -type d -path "*/skills/*" 2>/dev/null | head -1)"' in text, "expected to find: " + '[ ! -d "$NANOSTACK_ROOT" ] && NANOSTACK_ROOT="$(find "$HOME/.claude" -name "nanostack" -type d -path "*/skills/*" 2>/dev/null | head -1)"'[:80]

