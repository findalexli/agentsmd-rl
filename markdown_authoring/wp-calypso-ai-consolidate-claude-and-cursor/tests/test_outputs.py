"""Behavioral checks for wp-calypso-ai-consolidate-claude-and-cursor (markdown_authoring task).

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
    text = _read('.claude/rules/e2e-testing.md')
    assert '.claude/rules/e2e-testing.md' in text, "expected to find: " + '.claude/rules/e2e-testing.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/a4a.mdc')
    assert '.cursor/rules/a4a.mdc' in text, "expected to find: " + '.cursor/rules/a4a.mdc'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/calypso-client.mdc')
    assert '.cursor/rules/calypso-client.mdc' in text, "expected to find: " + '.cursor/rules/calypso-client.mdc'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/dashboard.mdc')
    assert '.cursor/rules/dashboard.mdc' in text, "expected to find: " + '.cursor/rules/dashboard.mdc'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('client/AGENTS.md')
    assert 'client/AGENTS.md' in text, "expected to find: " + 'client/AGENTS.md'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('client/CLAUDE.md')
    assert 'client/CLAUDE.md' in text, "expected to find: " + 'client/CLAUDE.md'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('client/a8c-for-agencies/AGENTS.md')
    assert 'client/a8c-for-agencies/AGENTS.md' in text, "expected to find: " + 'client/a8c-for-agencies/AGENTS.md'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('client/a8c-for-agencies/CLAUDE.md')
    assert 'client/a8c-for-agencies/CLAUDE.md' in text, "expected to find: " + 'client/a8c-for-agencies/CLAUDE.md'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('client/dashboard/AGENTS.md')
    assert '- **Purpose**: Ensures proper environment configuration (dev vs production hostnames)' in text, "expected to find: " + '- **Purpose**: Ensures proper environment configuration (dev vs production hostnames)'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('client/dashboard/AGENTS.md')
    assert "- **Import**: Use `import { wpcomLink } from '@automattic/dashboard/utils/link'`" in text, "expected to find: " + "- **Import**: Use `import { wpcomLink } from '@automattic/dashboard/utils/link'`"[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('client/dashboard/AGENTS.md')
    assert '- **Purpose**: Ensures correct behaviour when exiting the checkout screen' in text, "expected to find: " + '- **Purpose**: Ensures correct behaviour when exiting the checkout screen'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('client/dashboard/CLAUDE.md')
    assert 'client/dashboard/CLAUDE.md' in text, "expected to find: " + 'client/dashboard/CLAUDE.md'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('test/e2e/AGENTS.md')
    assert '- docs-new/ - New Playwright Test framework documentation' in text, "expected to find: " + '- docs-new/ - New Playwright Test framework documentation'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('test/e2e/AGENTS.md')
    assert '- Follow the patterns and style guide in docs-new/' in text, "expected to find: " + '- Follow the patterns and style guide in docs-new/'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('test/e2e/AGENTS.md')
    assert '### Legacy Framework (Playwright + Jest runner)' in text, "expected to find: " + '### Legacy Framework (Playwright + Jest runner)'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('test/e2e/CLAUDE.md')
    assert 'test/e2e/CLAUDE.md' in text, "expected to find: " + 'test/e2e/CLAUDE.md'[:80]

