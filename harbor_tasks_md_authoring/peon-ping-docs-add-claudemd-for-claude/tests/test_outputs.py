"""Behavioral checks for peon-ping-docs-add-claudemd-for-claude (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/peon-ping")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **`peon.sh`** — Main hook script. Receives JSON event data on stdin from Claude Code, routes events via an embedded Python block that handles config loading, event parsing, sound selection, and stat' in text, "expected to find: " + '- **`peon.sh`** — Main hook script. Receives JSON event data on stdin from Claude Code, routes events via an embedded Python block that handles config loading, event parsing, sound selection, and stat'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Tests use [BATS](https://github.com/bats-core/bats-core) (Bash Automated Testing System). Test setup (`tests/setup.bash`) creates isolated temp directories with mock audio backends, manifests, and con' in text, "expected to find: " + 'Tests use [BATS](https://github.com/bats-core/bats-core) (Bash Automated Testing System). Test setup (`tests/setup.bash`) creates isolated temp directories with mock audio backends, manifests, and con'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'peon-ping is a Claude Code hook that plays game character voice lines and sends desktop notifications when Claude Code needs attention. It handles 5 hook events: `SessionStart`, `UserPromptSubmit`, `S' in text, "expected to find: " + 'peon-ping is a Claude Code hook that plays game character voice lines and sends desktop notifications when Claude Code needs attention. It handles 5 hook events: `SessionStart`, `UserPromptSubmit`, `S'[:80]

