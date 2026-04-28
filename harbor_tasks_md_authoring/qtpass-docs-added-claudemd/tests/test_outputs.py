"""Behavioral checks for qtpass-docs-added-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/qtpass")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Qt Test framework. Tests live in `tests/auto/` subdirectories: util, ui, model, settings, passwordconfig, filecontent, simpletransaction, gpgkeystate (all platforms); executor and integration are excl' in text, "expected to find: " + 'Qt Test framework. Tests live in `tests/auto/` subdirectories: util, ui, model, settings, passwordconfig, filecontent, simpletransaction, gpgkeystate (all platforms); executor and integration are excl'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'QtPass is a multi-platform GUI for [pass](https://www.passwordstore.org/), the standard Unix password manager. It supports Linux, BSD, macOS, and Windows, using either the `pass` command-line tool or ' in text, "expected to find: " + 'QtPass is a multi-platform GUI for [pass](https://www.passwordstore.org/), the standard Unix password manager. It supports Linux, BSD, macOS, and Windows, using either the `pass` command-line tool or '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**Signal/slot flow:** `MainWindow` calls `Pass` methods → `Pass` queues commands via `Executor` → `Executor` emits signals with stdout/stderr → `Pass` processes output and emits higher-level signals →' in text, "expected to find: " + '**Signal/slot flow:** `MainWindow` calls `Pass` methods → `Pass` queues commands via `Executor` → `Executor` emits signals with stdout/stderr → `Pass` processes output and emits higher-level signals →'[:80]

