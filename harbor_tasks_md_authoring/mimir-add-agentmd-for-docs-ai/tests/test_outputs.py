"""Behavioral checks for mimir-add-agentmd-for-docs-ai (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mimir")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "The immediate copy after a heading should introduce and provide an overview of what's covered in the section." in text, "expected to find: " + "The immediate copy after a heading should introduce and provide an overview of what's covered in the section."[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Write with verbs and nouns. Use minimal adjectives except when describing Grafana Labs products.' in text, "expected to find: " + 'Write with verbs and nouns. Use minimal adjectives except when describing Grafana Labs products.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Suggest and link to next steps and related resources at the end of the article, for example:' in text, "expected to find: " + 'Suggest and link to next steps and related resources at the end of the article, for example:'[:80]

