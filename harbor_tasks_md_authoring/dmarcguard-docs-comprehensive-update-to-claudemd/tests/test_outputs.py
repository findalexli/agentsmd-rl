"""Behavioral checks for dmarcguard-docs-comprehensive-update-to-claudemd (markdown_authoring task).

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
    text = _read('CLAUDE.md')
    assert 'A Go application that fetches DMARC reports from IMAP mailboxes, parses them, and displays them in a Vue.js dashboard. Also supports MCP (Model Context Protocol) for AI assistant integration.' in text, "expected to find: " + 'A Go application that fetches DMARC reports from IMAP mailboxes, parses them, and displays them in a Vue.js dashboard. Also supports MCP (Model Context Protocol) for AI assistant integration.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Environment variables: `IMAP_HOST`, `IMAP_PORT`, `IMAP_USERNAME`, `IMAP_PASSWORD`, `IMAP_MAILBOX`, `IMAP_USE_TLS`, `DATABASE_PATH`, `SERVER_HOST`, `SERVER_PORT`' in text, "expected to find: " + 'Environment variables: `IMAP_HOST`, `IMAP_PORT`, `IMAP_USERNAME`, `IMAP_PASSWORD`, `IMAP_MAILBOX`, `IMAP_USE_TLS`, `DATABASE_PATH`, `SERVER_HOST`, `SERVER_PORT`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "The Vue.js frontend is built to `dist/`, copied to `internal/api/dist/`, and embedded via Go's `embed` directive. The binary is self-contained." in text, "expected to find: " + "The Vue.js frontend is built to `dist/`, copied to `internal/api/dist/`, and embedded via Go's `embed` directive. The binary is self-contained."[:80]

