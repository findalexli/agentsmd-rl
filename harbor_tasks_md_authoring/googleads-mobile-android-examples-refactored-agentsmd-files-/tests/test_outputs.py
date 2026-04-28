"""Behavioral checks for googleads-mobile-android-examples-refactored-agentsmd-files- (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/googleads-mobile-android-examples")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('kotlin/advanced/APIDemo/.skills/gma-integrate/SKILL.md')
    assert '*   **Initialization**: **ALWAYS** call `MobileAds.initialize()` on a background' in text, "expected to find: " + '*   **Initialization**: **ALWAYS** call `MobileAds.initialize()` on a background'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('kotlin/advanced/APIDemo/.skills/gma-integrate/SKILL.md')
    assert '*   **Confirm Ad Type**: If the user asks for a "banner ad" without specifying a' in text, "expected to find: " + '*   **Confirm Ad Type**: If the user asks for a "banner ad" without specifying a'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('kotlin/advanced/APIDemo/.skills/gma-integrate/SKILL.md')
    assert '*   **Suggest Large Anchored Adaptive**: Suggest large anchored adaptive banners' in text, "expected to find: " + '*   **Suggest Large Anchored Adaptive**: Suggest large anchored adaptive banners'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('kotlin/advanced/APIDemo/.skills/gma-migrate/SKILL.md')
    assert '| Feature                                  | Old SDK Method Signature                                                                                                                     | GMA Next-Gen' in text, "expected to find: " + '| Feature                                  | Old SDK Method Signature                                                                                                                     | GMA Next-Gen'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('kotlin/advanced/APIDemo/.skills/gma-migrate/SKILL.md')
    assert '| **Core**                                 |                                                                                                                                              |             ' in text, "expected to find: " + '| **Core**                                 |                                                                                                                                              |             '[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('kotlin/advanced/APIDemo/.skills/gma-migrate/SKILL.md')
    assert '| MobileAds Initialization                 | `MobileAds.initialize(Context context, OnInitializationCompleteListener listener)`                                                           | `MobileAds.i' in text, "expected to find: " + '| MobileAds Initialization                 | `MobileAds.initialize(Context context, OnInitializationCompleteListener listener)`                                                           | `MobileAds.i'[:80]

