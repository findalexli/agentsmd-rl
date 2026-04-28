"""Behavioral checks for grafana-alerting-add-gh-in-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/grafana")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('public/app/features/alerting/unified/CLAUDE.md')
    assert 'When working on issues, PRs, or needing repository context, use the GitHub CLI (`gh`) to fetch information directly:' in text, "expected to find: " + 'When working on issues, PRs, or needing repository context, use the GitHub CLI (`gh`) to fetch information directly:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('public/app/features/alerting/unified/CLAUDE.md')
    assert '- **Understanding issue context**: Fetch issue descriptions, comments, and linked PRs' in text, "expected to find: " + '- **Understanding issue context**: Fetch issue descriptions, comments, and linked PRs'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('public/app/features/alerting/unified/CLAUDE.md')
    assert '- **Finding related work**: Search for similar issues or existing implementations' in text, "expected to find: " + '- **Finding related work**: Search for similar issues or existing implementations'[:80]

