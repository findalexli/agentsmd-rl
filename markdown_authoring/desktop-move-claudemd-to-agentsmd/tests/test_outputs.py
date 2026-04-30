"""Behavioral checks for desktop-move-claudemd-to-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/desktop")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Module-specific documentation lives in `AGENTS.md` files within each subdirectory.' in text, "expected to find: " + 'Module-specific documentation lives in `AGENTS.md` files within each subdirectory.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '# AGENTS.md — Mattermost Desktop App' in text, "expected to find: " + '# AGENTS.md — Mattermost Desktop App'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('src/app/AGENTS.md')
    assert 'src/app/AGENTS.md' in text, "expected to find: " + 'src/app/AGENTS.md'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('src/app/preload/AGENTS.md')
    assert 'src/app/preload/AGENTS.md' in text, "expected to find: " + 'src/app/preload/AGENTS.md'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('src/app/views/AGENTS.md')
    assert 'src/app/views/AGENTS.md' in text, "expected to find: " + 'src/app/views/AGENTS.md'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('src/common/AGENTS.md')
    assert 'src/common/AGENTS.md' in text, "expected to find: " + 'src/common/AGENTS.md'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('src/common/config/AGENTS.md')
    assert 'src/common/config/AGENTS.md' in text, "expected to find: " + 'src/common/config/AGENTS.md'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('src/main/AGENTS.md')
    assert 'src/main/AGENTS.md' in text, "expected to find: " + 'src/main/AGENTS.md'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('src/main/diagnostics/AGENTS.md')
    assert 'src/main/diagnostics/AGENTS.md' in text, "expected to find: " + 'src/main/diagnostics/AGENTS.md'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('src/main/notifications/AGENTS.md')
    assert 'src/main/notifications/AGENTS.md' in text, "expected to find: " + 'src/main/notifications/AGENTS.md'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('src/main/security/AGENTS.md')
    assert 'src/main/security/AGENTS.md' in text, "expected to find: " + 'src/main/security/AGENTS.md'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('src/renderer/AGENTS.md')
    assert 'src/renderer/AGENTS.md' in text, "expected to find: " + 'src/renderer/AGENTS.md'[:80]

