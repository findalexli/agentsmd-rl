"""Behavioral checks for openproject-revert-split-the-root-agentmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/openproject")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'bin/compose run                           # Start frontend in background, backend in foreground (for debugging with pry)' in text, "expected to find: " + 'bin/compose run                           # Start frontend in background, backend in foreground (for debugging with pry)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The Docker development environment uses configurations in `docker/dev/` and the `bin/compose` wrapper script.' in text, "expected to find: " + 'The Docker development environment uses configurations in `docker/dev/` and the `bin/compose` wrapper script.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'OpenProject supports two development setups: **Local** and **Docker**. Choose one based on your preference.' in text, "expected to find: " + 'OpenProject supports two development setups: **Local** and **Docker**. Choose one based on your preference.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('app/AGENTS.md')
    assert 'app/AGENTS.md' in text, "expected to find: " + 'app/AGENTS.md'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('app/CLAUDE.md')
    assert 'app/CLAUDE.md' in text, "expected to find: " + 'app/CLAUDE.md'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('config/AGENTS.md')
    assert 'config/AGENTS.md' in text, "expected to find: " + 'config/AGENTS.md'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('config/CLAUDE.md')
    assert 'config/CLAUDE.md' in text, "expected to find: " + 'config/CLAUDE.md'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('db/AGENTS.md')
    assert 'db/AGENTS.md' in text, "expected to find: " + 'db/AGENTS.md'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('db/CLAUDE.md')
    assert 'db/CLAUDE.md' in text, "expected to find: " + 'db/CLAUDE.md'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('docker/dev/AGENTS.md')
    assert 'docker/dev/AGENTS.md' in text, "expected to find: " + 'docker/dev/AGENTS.md'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('docker/dev/CLAUDE.md')
    assert 'docker/dev/CLAUDE.md' in text, "expected to find: " + 'docker/dev/CLAUDE.md'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('frontend/AGENTS.md')
    assert 'frontend/AGENTS.md' in text, "expected to find: " + 'frontend/AGENTS.md'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('frontend/CLAUDE.md')
    assert 'frontend/CLAUDE.md' in text, "expected to find: " + 'frontend/CLAUDE.md'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('spec/AGENTS.md')
    assert 'spec/AGENTS.md' in text, "expected to find: " + 'spec/AGENTS.md'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('spec/CLAUDE.md')
    assert 'spec/CLAUDE.md' in text, "expected to find: " + 'spec/CLAUDE.md'[:80]

