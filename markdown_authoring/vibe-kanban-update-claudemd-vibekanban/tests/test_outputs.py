"""Behavioral checks for vibe-kanban-update-claudemd-vibekanban (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/vibe-kanban")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `crates/`: Rust workspace crates — `server` (API + bins), `db` (SQLx models/migrations), `executors`, `services`, `utils`, `deployment`, `local-deployment`, `remote`.' in text, "expected to find: " + '- `crates/`: Rust workspace crates — `server` (API + bins), `db` (SQLx models/migrations), `executors`, `services`, `utils`, `deployment`, `local-deployment`, `remote`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `remote-frontend/`: Remote deployment frontend.' in text, "expected to find: " + '- `remote-frontend/`: Remote deployment frontend.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `docs/`: Documentation files.' in text, "expected to find: " + '- `docs/`: Documentation files.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

