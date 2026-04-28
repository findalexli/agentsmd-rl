"""Behavioral checks for js-recall-fix-update-cursorrules-detailing-efficient (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/js-recall")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/api-specific-config.mdc')
    assert '- **Method Complexity:** If a service method has 3+ distinct steps (especially if labeled as "Step 1", "Step 2", etc.), consider extracting each step into a private helper method' in text, "expected to find: " + '- **Method Complexity:** If a service method has 3+ distinct steps (especially if labeled as "Step 1", "Step 2", etc.), consider extracting each step into a private helper method'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/api-specific-config.mdc')
    assert '- **Batch Operation Helpers:** Create reusable helpers for batch operations (batch fetching, batch processing) that can be shared across methods' in text, "expected to find: " + '- **Batch Operation Helpers:** Create reusable helpers for batch operations (batch fetching, batch processing) that can be shared across methods'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/api-specific-config.mdc')
    assert '- **Retry Logic Separation:** Extract retry logic with exponential backoff into dedicated helper methods rather than inline in business logic' in text, "expected to find: " + '- **Retry Logic Separation:** Extract retry logic with exponential backoff into dedicated helper methods rather than inline in business logic'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/org-general-practices.mdc')
    assert '- **Extract Helper Methods:** When a function exceeds ~30-40 lines or has distinct logical sections (e.g., validation, processing, output), extract helper methods. If you have numbered steps in commen' in text, "expected to find: " + '- **Extract Helper Methods:** When a function exceeds ~30-40 lines or has distinct logical sections (e.g., validation, processing, output), extract helper methods. If you have numbered steps in commen'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/org-general-practices.mdc')
    assert "- **Don't Compute What You Don't Need:** Avoid building intermediate data structures (arrays, objects) just to check a property. For example, don't build an array just to check if it's empty - use a b" in text, "expected to find: " + "- **Don't Compute What You Don't Need:** Avoid building intermediate data structures (arrays, objects) just to check a property. For example, don't build an array just to check if it's empty - use a b"[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/org-general-practices.mdc')
    assert '- **Early Exit Strategies:** Prefer methods that can exit early (`.some()`, `.every()`, `.find()`) over methods that process everything (`.filter().length`, `.map()`) when you just need a boolean or s' in text, "expected to find: " + '- **Early Exit Strategies:** Prefer methods that can exit early (`.some()`, `.every()`, `.find()`) over methods that process everything (`.filter().length`, `.map()`) when you just need a boolean or s'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/org-typescript-standards.mdc')
    assert '- Avoid `.filter().length === 0` or `.filter().length > 0` when `.some()` or `.every()` would suffice' in text, "expected to find: " + '- Avoid `.filter().length === 0` or `.filter().length > 0` when `.some()` or `.every()` would suffice'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/org-typescript-standards.mdc')
    assert '- Return discriminated unions or Result types from helpers to make error handling explicit' in text, "expected to find: " + '- Return discriminated unions or Result types from helpers to make error handling explicit'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/org-typescript-standards.mdc')
    assert "- Don't build arrays just to check emptiness or count - use boolean checks where possible" in text, "expected to find: " + "- Don't build arrays just to check emptiness or count - use boolean checks where possible"[:80]

