"""Behavioral checks for react-native-navigation-add-and-update-ai-coding (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/react-native-navigation")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/rn-version-upgrade.md')
    assert "12. **Don't just follow existing patterns — research better ones** -- When fixing a compilation error, don't blindly copy the guarding pattern already used in the codebase. The existing pattern may pr" in text, "expected to find: " + "12. **Don't just follow existing patterns — research better ones** -- When fixing a compilation error, don't blindly copy the guarding pattern already used in the codebase. The existing pattern may pr"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/rn-version-upgrade.md')
    assert '**Pattern 3: Test infrastructure** -- Test/mock classes that extend RN framework classes (e.g., `SimpleView extends ReactView`) may need refactoring if the parent class behavior changed. Also check Ro' in text, "expected to find: " + '**Pattern 3: Test infrastructure** -- Test/mock classes that extend RN framework classes (e.g., `SimpleView extends ReactView`) may need refactoring if the parent class behavior changed. Also check Ro'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/rn-version-upgrade.md')
    assert '**If the new RN version strips legacy headers from the xcframework** (look for `RCT_REMOVE_LEGACY_ARCH` changes in the RN release), identify ALL iOS files importing legacy-only headers and plan to gua' in text, "expected to find: " + '**If the new RN version strips legacy headers from the xcframework** (look for `RCT_REMOVE_LEGACY_ARCH` changes in the RN release), identify ALL iOS files importing legacy-only headers and plan to gua'[:80]

