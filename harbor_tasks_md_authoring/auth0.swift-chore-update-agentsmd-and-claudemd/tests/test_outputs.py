"""Behavioral checks for auth0.swift-chore-update-agentsmd-and-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/auth0.swift")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **`Auth0.plist` vs `Info.plist`**: The SDK reads `ClientId`/`Domain` from `Auth0.plist` in test targets; production apps typically use `Auth0.plist` or pass values programmatically' in text, "expected to find: " + '- **`Auth0.plist` vs `Info.plist`**: The SDK reads `ClientId`/`Domain` from `Auth0.plist` in test targets; production apps typically use `Auth0.plist` or pass values programmatically'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Callback URL mismatch**: The URL scheme in `Auth0 Dashboard` must match `CFBundleURLTypes` in `Info.plist` (format: `com.example.app://YOUR_DOMAIN/ios/com.example.app/callback`)' in text, "expected to find: " + '- **Callback URL mismatch**: The URL scheme in `Auth0 Dashboard` must match `CFBundleURLTypes` in `Info.plist` (format: `com.example.app://YOUR_DOMAIN/ios/com.example.app/callback`)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Missing `@MainActor`**: UI updates from SDK callbacks must be dispatched on the main actor — the SDK does this internally, but calling code must not assume a background thread' in text, "expected to find: " + '- **Missing `@MainActor`**: UI updates from SDK callbacks must be dispatched on the main actor — the SDK does this internally, but calling code must not assume a background thread'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'See @AGENTS.md for all coding guidelines, commands, project structure, code style, testing conventions, and boundaries.' in text, "expected to find: " + 'See @AGENTS.md for all coding guidelines, commands, project structure, code style, testing conventions, and boundaries.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '# Claude Guidelines for Auth0.swift' in text, "expected to find: " + '# Claude Guidelines for Auth0.swift'[:80]

