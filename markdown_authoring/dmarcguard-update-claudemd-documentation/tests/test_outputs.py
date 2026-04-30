"""Behavioral checks for dmarcguard-update-claudemd-documentation (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dmarcguard")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('claude.md')
    assert 'A Go application that fetches DMARC reports from IMAP mailboxes, parses them, and displays them in a Vue.js dashboard.' in text, "expected to find: " + 'A Go application that fetches DMARC reports from IMAP mailboxes, parses them, and displays them in a Vue.js dashboard.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('claude.md')
    assert '- `internal/config/config.go` - Configuration loading (JSON file + env vars)' in text, "expected to find: " + '- `internal/config/config.go` - Configuration loading (JSON file + env vars)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('claude.md')
    assert '│   ├── config/            # Configuration management (JSON + env vars)' in text, "expected to find: " + '│   ├── config/            # Configuration management (JSON + env vars)'[:80]

