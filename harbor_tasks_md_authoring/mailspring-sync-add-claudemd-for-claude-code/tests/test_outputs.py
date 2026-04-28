"""Behavioral checks for mailspring-sync-add-claudemd-for-claude-code (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mailspring-sync")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Mailspring-Sync is the native C++11 sync engine for the Mailspring email client. It handles email, contact, and calendar synchronization via IMAP/SMTP using MailCore2, storing data in SQLite with a JS' in text, "expected to find: " + 'Mailspring-Sync is the native C++11 sync engine for the Mailspring email client. It handles email, contact, and calendar synchronization via IMAP/SMTP using MailCore2, storing data in SQLite with a JS'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**Delta Coalescing:** Multiple saves of the same object within a flush window are merged—only the final state is emitted, with keys merged to preserve conditionally-included fields (e.g., `message.bod' in text, "expected to find: " + '**Delta Coalescing:** Multiple saves of the same object within a flush window are merged—only the final state is emitted, with keys merged to preserve conditionally-included fields (e.g., `message.bod'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- `MailStore`: SQLite database wrapper with template-based queries. Uses "fat" rows with a `data` JSON column plus indexed columns for queryable fields. See Reactive Data Flow above.' in text, "expected to find: " + '- `MailStore`: SQLite database wrapper with template-based queries. Uses "fat" rows with a `data` JSON column plus indexed columns for queryable fields. See Reactive Data Flow above.'[:80]

