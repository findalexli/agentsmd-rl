"""Behavioral checks for sentry-bugbot-add-disclosure-to-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/sentry")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('static/AGENTS.md')
    assert 'Use <Text> from `@sentry/scraps/text` for text styling instead of styled components that handle typography features like color, overflow, font-size, font-weight.' in text, "expected to find: " + 'Use <Text> from `@sentry/scraps/text` for text styling instead of styled components that handle typography features like color, overflow, font-size, font-weight.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('static/AGENTS.md')
    assert 'Use <Flex> from `@sentry/scraps/layout` for elements that require flex layout as opposed to styled components with `display: flex`.' in text, "expected to find: " + 'Use <Flex> from `@sentry/scraps/layout` for elements that require flex layout as opposed to styled components with `display: flex`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('static/AGENTS.md')
    assert 'Use <Grid> from `@sentry/scraps/layout` for elements that require grid layout as opposed to styled components with `display: grid`' in text, "expected to find: " + 'Use <Grid> from `@sentry/scraps/layout` for elements that require grid layout as opposed to styled components with `display: grid`'[:80]

