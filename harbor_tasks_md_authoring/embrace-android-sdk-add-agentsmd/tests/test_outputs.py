"""Behavioral checks for embrace-android-sdk-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/embrace-android-sdk")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **`embrace-android-infra`** - JVM-only core infrastructure types used across most modules (e.g., `InternalLogger`, `BackgroundWorker`,' in text, "expected to find: " + '- **`embrace-android-infra`** - JVM-only core infrastructure types used across most modules (e.g., `InternalLogger`, `BackgroundWorker`,'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '| Plugin                             | Applies to                  | What it does                                                   |' in text, "expected to find: " + '| Plugin                             | Applies to                  | What it does                                                   |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '| `embrace-common-conventions`       | All modules                 | Detekt, compiler settings, JVM target                          |' in text, "expected to find: " + '| `embrace-common-conventions`       | All modules                 | Detekt, compiler settings, JVM target                          |'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Read and follow all conventions in [AGENTS.md](./AGENTS.md).' in text, "expected to find: " + 'Read and follow all conventions in [AGENTS.md](./AGENTS.md).'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '# Claude Code Configuration' in text, "expected to find: " + '# Claude Code Configuration'[:80]

