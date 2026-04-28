"""Behavioral checks for mailspring-add-comprehensive-claudemd-with-architecture (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mailspring")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**Important:** The UI is read-only with respect to the database. All database modifications happen in the C++ sync engine (Mailspring-Sync). The Electron app requests changes via Tasks, and the sync e' in text, "expected to find: " + '**Important:** The UI is read-only with respect to the database. All database modifications happen in the C++ sync engine (Mailspring-Sync). The Electron app requests changes via Tasks, and the sync e'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "The `MailsyncBridge` (in main window only) manages sync process lifecycle, listens to `Actions.queueTask`, and forwards tasks to the appropriate account's sync process." in text, "expected to find: " + "The `MailsyncBridge` (in main window only) manages sync process lifecycle, listens to `Actions.queueTask`, and forwards tasks to the appropriate account's sync process."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Mailspring is an Electron-based email client written in TypeScript with React. It uses a plugin architecture where features are implemented as internal packages.' in text, "expected to find: " + 'Mailspring is an Electron-based email client written in TypeScript with React. It uses a plugin architecture where features are implemented as internal packages.'[:80]

