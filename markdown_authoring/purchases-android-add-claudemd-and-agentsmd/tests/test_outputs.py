"""Behavioral checks for purchases-android-add-claudemd-and-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/purchases-android")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **`@InternalRevenueCatAPI`** - APIs that are public only to be accessible by other modules or hybrid SDKs, not intended for external developer use' in text, "expected to find: " + '- **`@InternalRevenueCatAPI`** - APIs that are public only to be accessible by other modules or hybrid SDKs, not intended for external developer use'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **`:ui:revenuecatui`** - Jetpack Compose UI module for paywalls and customer center (min SDK 24, depends on `:purchases`)' in text, "expected to find: " + '- **`:ui:revenuecatui`** - Jetpack Compose UI module for paywalls and customer center (min SDK 24, depends on `:purchases`)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **`@ExperimentalPreviewRevenueCatPurchasesAPI`** - Public APIs for developers that may change before being made stable' in text, "expected to find: " + '- **`@ExperimentalPreviewRevenueCatPurchasesAPI`** - Public APIs for developers that may change before being made stable'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

