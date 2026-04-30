"""Behavioral checks for auth0.swift-added-agentsmd-file (markdown_authoring task).

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
    assert '**Auth0.swift** is an idiomatic Swift SDK for integrating Auth0 authentication and authorization into Apple platform applications (iOS, macOS, tvOS, watchOS). The SDK provides a comprehensive solution' in text, "expected to find: " + '**Auth0.swift** is an idiomatic Swift SDK for integrating Auth0 authentication and authorization into Apple platform applications (iOS, macOS, tvOS, watchOS). The SDK provides a comprehensive solution'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- **Bundle Identifier**: The callback URL in the Auth0 Dashboard must match the App's Bundle ID format (e.g., `com.example.app://YOUR_DOMAIN/ios/com.example.app/callback`)." in text, "expected to find: " + "- **Bundle Identifier**: The callback URL in the Auth0 Dashboard must match the App's Bundle ID format (e.g., `com.example.app://YOUR_DOMAIN/ios/com.example.app/callback`)."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Protocol-Oriented**: Heavy use of protocols to define API contracts (`Authentication`, `WebAuth`, `CredentialsStorage`).' in text, "expected to find: " + '- **Protocol-Oriented**: Heavy use of protocols to define API contracts (`Authentication`, `WebAuth`, `CredentialsStorage`).'[:80]

