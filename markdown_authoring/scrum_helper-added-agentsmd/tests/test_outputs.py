"""Behavioral checks for scrum_helper-added-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/scrum-helper")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('agents.md')
    assert '- You must be able to explain what changed, why it changed, and how it interacts with existing code paths (popup, service worker/background, content scripts, GitHub API, i18n, and browser-specific bui' in text, "expected to find: " + '- You must be able to explain what changed, why it changed, and how it interacts with existing code paths (popup, service worker/background, content scripts, GitHub API, i18n, and browser-specific bui'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('agents.md')
    assert 'Scrum Helper accepts AI-assisted contributions, but all submissions must meet project standards. The contributor submitting the PR is fully responsible for correctness, scope, and validation.' in text, "expected to find: " + 'Scrum Helper accepts AI-assisted contributions, but all submissions must meet project standards. The contributor submitting the PR is fully responsible for correctness, scope, and validation.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('agents.md')
    assert '- Validate edge cases relevant to your change (empty states, missing token/auth, API failures, rate limits, and large result sets where applicable).' in text, "expected to find: " + '- Validate edge cases relevant to your change (empty states, missing token/auth, API failures, rate limits, and large result sets where applicable).'[:80]

