"""Behavioral checks for sentry-fixanalytics-fixup-claudemd-for-new (markdown_authoring task).

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
    text = _read('CLAUDE.md')
    assert 'from sentry.analytics.events.feature_used import FeatureUsedEvent  # does not exist, only for demonstration purposes' in text, "expected to find: " + 'from sentry.analytics.events.feature_used import FeatureUsedEvent  # does not exist, only for demonstration purposes'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'feature="new-dashboard",' in text, "expected to find: " + 'feature="new-dashboard",'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'organization_id=org.id,' in text, "expected to find: " + 'organization_id=org.id,'[:80]

