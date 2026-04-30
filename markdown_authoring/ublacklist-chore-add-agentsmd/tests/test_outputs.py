"""Behavioral checks for ublacklist-chore-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ublacklist")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'uBlacklist is a browser extension that blocks specific sites from appearing in search engine results. It supports Chrome, Firefox, and Safari, with cloud sync via Google Drive, Dropbox, WebDAV, and br' in text, "expected to find: " + 'uBlacklist is a browser extension that blocks specific sites from appearing in search engine results. It supports Chrome, Firefox, and Safari, with cloud sync via Google Drive, Dropbox, WebDAV, and br'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `src/scripts/background.ts` - Service worker/background script handling sync, subscriptions, cloud connections, and content script registration' in text, "expected to find: " + '- `src/scripts/background.ts` - Service worker/background script handling sync, subscriptions, cloud connections, and content script registration'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `src/scripts/serpinfo/content-script.ts` - Content script injected into search engine result pages (SERPs) to filter/block results' in text, "expected to find: " + '- `src/scripts/serpinfo/content-script.ts` - Content script injected into search engine result pages (SERPs) to filter/block results'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

