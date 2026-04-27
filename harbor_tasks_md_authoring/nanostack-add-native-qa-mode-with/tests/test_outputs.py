"""Behavioral checks for nanostack-add-native-qa-mode-with (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nanostack")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('qa/SKILL.md')
    assert 'description: Use to verify that code works correctly — browser-based testing with Playwright, native app testing with computer use, CLI testing, API testing, or root-cause debugging. Supports --quick,' in text, "expected to find: " + 'description: Use to verify that code works correctly — browser-based testing with Playwright, native app testing with computer use, CLI testing, API testing, or root-cause debugging. Supports --quick,'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('qa/SKILL.md')
    assert '**Prefer the most precise tool.** For web apps, use Playwright (faster, headless, scriptable). Use computer use only when the target has no CLI, no API, and no browser interface. Computer use is the b' in text, "expected to find: " + '**Prefer the most precise tool.** For web apps, use Playwright (faster, headless, scriptable). Use computer use only when the target has no CLI, no API, and no browser interface. Computer use is the b'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('qa/SKILL.md')
    assert '**When computer use is not available** (Linux, Windows, no Pro/Max plan, non-interactive session), skip Native QA and report: "Native QA skipped: computer use not available. Manual testing required fo' in text, "expected to find: " + '**When computer use is not available** (Linux, Windows, no Pro/Max plan, non-interactive session), skip Native QA and report: "Native QA skipped: computer use not available. Manual testing required fo'[:80]

