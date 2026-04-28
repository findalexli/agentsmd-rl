"""Behavioral checks for sentry-symfony-add-cursor-agent-rules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/sentry-symfony")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/release-process.mdc')
    assert '- Use format: `- Description [(#PR)](mdc:https:/github.com/getsentry/sentry-symfony/pull/PR)`' in text, "expected to find: " + '- Use format: `- Description [(#PR)](mdc:https:/github.com/getsentry/sentry-symfony/pull/PR)`'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/release-process.mdc')
    assert 'The Sentry SDK team is happy to announce the immediate availability of Sentry PHP SDK vX.Y.Z.' in text, "expected to find: " + 'The Sentry SDK team is happy to announce the immediate availability of Sentry PHP SDK vX.Y.Z.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/release-process.mdc')
    assert '- Documentation/misc changes [(#1236)](mdc:https:/github.com/getsentry/sentry-php/pull/1236)' in text, "expected to find: " + '- Documentation/misc changes [(#1236)](mdc:https:/github.com/getsentry/sentry-php/pull/1236)'[:80]

