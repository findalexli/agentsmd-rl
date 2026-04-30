"""Behavioral checks for sentry-java-add-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/sentry-java")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'This is the Sentry Java/Android SDK - a comprehensive error monitoring and performance tracking SDK for Java and Android applications. The repository contains multiple modules for different integratio' in text, "expected to find: " + 'This is the Sentry Java/Android SDK - a comprehensive error monitoring and performance tracking SDK for Java and Android applications. The repository contains multiple modules for different integratio'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Scopes and Hub Management**: See `.cursor/rules/scopes.mdc` for details on `IScopes`, scope types (global/isolation/current), thread-local storage, forking behavior, and v7→v8 migration patterns' in text, "expected to find: " + '- **Scopes and Hub Management**: See `.cursor/rules/scopes.mdc` for details on `IScopes`, scope types (global/isolation/current), thread-local storage, forking behavior, and v7→v8 migration patterns'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'When working on these specific areas, read the corresponding cursor rule file first to understand the detailed architecture, then proceed with implementation.' in text, "expected to find: " + 'When working on these specific areas, read the corresponding cursor rule file first to understand the detailed architecture, then proceed with implementation.'[:80]

