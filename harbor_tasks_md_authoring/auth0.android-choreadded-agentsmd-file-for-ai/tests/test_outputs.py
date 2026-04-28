"""Behavioral checks for auth0.android-choreadded-agentsmd-file-for-ai (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/auth0.android")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '.github/copilot-instructions.md' in text, "expected to find: " + '.github/copilot-instructions.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Auth0.Android** is a native Android SDK for integrating Auth0 authentication and authorization into Android applications. The SDK provides a comprehensive solution for:' in text, "expected to find: " + '**Auth0.Android** is a native Android SDK for integrating Auth0 authentication and authorization into Android applications. The SDK provides a comprehensive solution for:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This document provides context and guidelines for AI coding assistants working with the Auth0.Android SDK codebase.' in text, "expected to find: " + 'This document provides context and guidelines for AI coding assistants working with the Auth0.Android SDK codebase.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Builder Pattern**: Used extensively for web based authentication flows (e.g., `WebAuthProvider.login()`)' in text, "expected to find: " + '- **Builder Pattern**: Used extensively for web based authentication flows (e.g., `WebAuthProvider.login()`)'[:80]

