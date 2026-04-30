"""Behavioral checks for hermes-swift-mac-docs-add-claudemd-context-and (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/hermes-swift-mac")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) {' in text, "expected to find: " + 'func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) {'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {' in text, "expected to find: " + 'func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Never codesign the DMG before notarization — notarize the app bundle, then package into DMG' in text, "expected to find: " + '- Never codesign the DMG before notarization — notarize the app bundle, then package into DMG'[:80]

