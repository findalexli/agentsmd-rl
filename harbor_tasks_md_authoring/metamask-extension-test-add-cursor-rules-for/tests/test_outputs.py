"""Behavioral checks for metamask-extension-test-add-cursor-rules-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/metamask-extension")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('test/e2e/.cursor/rules/e2e-testing-guidelines.mdc')
    assert 'For complex user workflows that span multiple pages, create **Flow Objects** that orchestrate interactions between multiple Page Objects. Flows should encapsulate complete user journeys and promote re' in text, "expected to find: " + 'For complex user workflows that span multiple pages, create **Flow Objects** that orchestrate interactions between multiple Page Objects. Flows should encapsulate complete user journeys and promote re'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('test/e2e/.cursor/rules/e2e-testing-guidelines.mdc')
    assert '- **Driver** (`/test/e2e/webdriver/driver.js`) - Custom Selenium WebDriver wrapper providing enhanced element interactions, waiting strategies, and browser management' in text, "expected to find: " + '- **Driver** (`/test/e2e/webdriver/driver.js`) - Custom Selenium WebDriver wrapper providing enhanced element interactions, waiting strategies, and browser management'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('test/e2e/.cursor/rules/e2e-testing-guidelines.mdc')
    assert '- **Flow Objects** (`/test/e2e/page-objects/flows/`) - Multi-step user workflow implementations with Page Object Model pattern (login, onboarding, transaction flows)' in text, "expected to find: " + '- **Flow Objects** (`/test/e2e/page-objects/flows/`) - Multi-step user workflow implementations with Page Object Model pattern (login, onboarding, transaction flows)'[:80]

