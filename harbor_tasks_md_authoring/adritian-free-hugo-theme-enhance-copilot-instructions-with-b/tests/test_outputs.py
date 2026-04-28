"""Behavioral checks for adritian-free-hugo-theme-enhance-copilot-instructions-with-b (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/adritian-free-hugo-theme")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'This is a **Hugo theme** for personal websites/portfolios, not a standalone site (although a example site is provided, to demonstrate the usage of the theme itself). The theme provides layouts, stylin' in text, "expected to find: " + 'This is a **Hugo theme** for personal websites/portfolios, not a standalone site (although a example site is provided, to demonstrate the usage of the theme itself). The theme provides layouts, stylin'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'This is a **Hugo theme** for personal websites/portfolios, not a standalone site. The theme provides layouts, styling, and functionality that users import via Hugo modules or as a git submodule.' in text, "expected to find: " + 'This is a **Hugo theme** for personal websites/portfolios, not a standalone site. The theme provides layouts, styling, and functionality that users import via Hugo modules or as a git submodule.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'When modifying layouts or adding features, ensure corresponding E2E tests exist in `tests/e2e/`.' in text, "expected to find: " + 'When modifying layouts or adding features, ensure corresponding E2E tests exist in `tests/e2e/`.'[:80]

