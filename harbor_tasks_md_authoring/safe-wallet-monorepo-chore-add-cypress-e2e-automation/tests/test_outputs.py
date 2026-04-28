"""Behavioral checks for safe-wallet-monorepo-chore-add-cypress-e2e-automation (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/safe-wallet-monorepo")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/cypress-e2e.mdc')
    assert "- **MANDATORY**: Helper functions that are specific to a page's functionality should be located in that page's `.pages.js` file, not in `main.page.js`" in text, "expected to find: " + "- **MANDATORY**: Helper functions that are specific to a page's functionality should be located in that page's `.pages.js` file, not in `main.page.js`"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/cypress-e2e.mdc')
    assert "6. **Place helper functions in proper page files**: Helper functions specific to a page must be in that page's `.pages.js` file, not in `main.page.js`" in text, "expected to find: " + "6. **Place helper functions in proper page files**: Helper functions specific to a page must be in that page's `.pages.js` file, not in `main.page.js`"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/cypress-e2e.mdc')
    assert '- **MANDATORY**: Before creating any new function, AI MUST check if a similar function already exists in other page files' in text, "expected to find: " + '- **MANDATORY**: Before creating any new function, AI MUST check if a similar function already exists in other page files'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **IMPORTANT**: Follow the Cypress E2E automation rules in `.cursor/rules/cypress-e2e.mdc` when writing or modifying tests' in text, "expected to find: " + '- **IMPORTANT**: Follow the Cypress E2E automation rules in `.cursor/rules/cypress-e2e.mdc` when writing or modifying tests'[:80]

