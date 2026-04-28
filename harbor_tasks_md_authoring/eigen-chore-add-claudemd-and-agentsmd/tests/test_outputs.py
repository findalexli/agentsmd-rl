"""Behavioral checks for eigen-chore-add-claudemd-and-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/eigen")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "Eigen is Artsy's mobile app — a bare React Native application that uses the Expo sdk, available on both iOS and Android, that powers the [Artsy](https://www.artsy.net) marketplace for discovering and " in text, "expected to find: " + "Eigen is Artsy's mobile app — a bare React Native application that uses the Expo sdk, available on both iOS and Android, that powers the [Artsy](https://www.artsy.net) marketplace for discovering and "[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- Legacy `@ts-expect-error STRICTNESS_MIGRATION` comments exist throughout the codebase — remove them when touching affected code, but only if it's a straightforward change." in text, "expected to find: " + "- Legacy `@ts-expect-error STRICTNESS_MIGRATION` comments exist throughout the codebase — remove them when touching affected code, but only if it's a straightforward change."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- When adding a screen with a corresponding artsy.net page, match the route path and enable deep linking (add to `AndroidManifest.xml` for Android)' in text, "expected to find: " + '- When adding a screen with a corresponding artsy.net page, match the route path and enable deep linking (add to `AndroidManifest.xml` for Android)'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'See @AGENTS.md' in text, "expected to find: " + 'See @AGENTS.md'[:80]

