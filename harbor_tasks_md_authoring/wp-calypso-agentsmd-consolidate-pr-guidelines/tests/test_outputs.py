"""Behavioral checks for wp-calypso-agentsmd-consolidate-pr-guidelines (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/wp-calypso")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/pr.md')
    assert '.claude/rules/pr.md' in text, "expected to find: " + '.claude/rules/pr.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Include all checklist items from .github/PULL_REQUEST_TEMPLATE.md. Only mark items as completed (`[x]`) if they actually apply; leave inapplicable items unchecked (`[ ]`).' in text, "expected to find: " + '- Include all checklist items from .github/PULL_REQUEST_TEMPLATE.md. Only mark items as completed (`[x]`) if they actually apply; leave inapplicable items unchecked (`[ ]`).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Create PRs as draft. Follow the template in .github/PULL_REQUEST_TEMPLATE.md.' in text, "expected to find: " + '- Create PRs as draft. Follow the template in .github/PULL_REQUEST_TEMPLATE.md.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Use Linear issue IDs (e.g., `LIN-123`) instead of full Linear URLs.' in text, "expected to find: " + '- Use Linear issue IDs (e.g., `LIN-123`) instead of full Linear URLs.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

