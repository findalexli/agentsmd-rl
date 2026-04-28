"""Behavioral checks for metamask-mobile-chore-updating-unit-testing-cursor (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/metamask-mobile")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/unit-testing-guidelines.mdc')
    assert '**ALL `@metamask/design-system-react-native` and `app/component-library` components support child prop objects for passing testIDs to internal elements.** This is a universal design pattern - prefer n' in text, "expected to find: " + '**ALL `@metamask/design-system-react-native` and `app/component-library` components support child prop objects for passing testIDs to internal elements.** This is a universal design pattern - prefer n'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/unit-testing-guidelines.mdc')
    assert '**If you need to add a testID to one of these components, check for child prop objects first.** Most components support this functionality. If not available, suggest adjusting the component to support' in text, "expected to find: " + '**If you need to add a testID to one of these components, check for child prop objects first.** Most components support this functionality. If not available, suggest adjusting the component to support'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/unit-testing-guidelines.mdc')
    assert '**Prefer not to mock `@metamask/design-system-react-native` or `app/component-library` components just to inject testIDs.** All these components support testIDs via:' in text, "expected to find: " + '**Prefer not to mock `@metamask/design-system-react-native` or `app/component-library` components just to inject testIDs.** All these components support testIDs via:'[:80]

