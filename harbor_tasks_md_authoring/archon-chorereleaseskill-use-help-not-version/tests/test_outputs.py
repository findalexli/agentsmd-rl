"""Behavioral checks for archon-chorereleaseskill-use-help-not-version (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/archon")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/release/SKILL.md')
    assert '# path depends on BUNDLED_IS_BINARY=true, which is set by scripts/build-binaries.sh' in text, "expected to find: " + '# path depends on BUNDLED_IS_BINARY=true, which is set by scripts/build-binaries.sh'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/release/SKILL.md')
    assert "# — but we're doing a bare `bun build --compile` here to keep the smoke fast," in text, "expected to find: " + "# — but we're doing a bare `bun build --compile` here to keep the smoke fast,"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/release/SKILL.md')
    assert '# branch of version.ts which tries to read package.json from a path that only' in text, "expected to find: " + '# branch of version.ts which tries to read package.json from a path that only'[:80]

