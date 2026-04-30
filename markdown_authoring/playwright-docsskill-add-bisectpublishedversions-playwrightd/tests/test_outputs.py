"""Behavioral checks for playwright-docsskill-add-bisectpublishedversions-playwrightd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/playwright")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/playwright-dev/SKILL.md')
    assert '- [Bisecting Across Published Versions](bisect-published-versions.md) — reproduce regressions side-by-side from npm and diff `node_modules/playwright/lib/` between versions' in text, "expected to find: " + '- [Bisecting Across Published Versions](bisect-published-versions.md) — reproduce regressions side-by-side from npm and diff `node_modules/playwright/lib/` between versions'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/playwright-dev/bisect-published-versions.md')
    assert 'When a user reports a regression between two published Playwright versions (e.g. "works in 1.58, broken in 1.59.1"), reproduce both side by side from npm — do **not** try to bisect against the monorep' in text, "expected to find: " + 'When a user reports a regression between two published Playwright versions (e.g. "works in 1.58, broken in 1.59.1"), reproduce both side by side from npm — do **not** try to bisect against the monorep'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/playwright-dev/bisect-published-versions.md')
    assert "- **Don't try to map the bug to monorepo source first.** The shipped JS is what the user is running; source may have already been refactored or fixed on `main`. Investigate `node_modules/` first, then" in text, "expected to find: " + "- **Don't try to map the bug to monorepo source first.** The shipped JS is what the user is running; source may have already been refactored or fixed on `main`. Investigate `node_modules/` first, then"[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/playwright-dev/bisect-published-versions.md')
    assert "For stack-trace bugs in particular, a `console.log(new Error().stack)` inserted at the capture site (e.g. inside `expect.js`'s `captureRawStack`) instantly shows whether the issue is microtask-boundar" in text, "expected to find: " + "For stack-trace bugs in particular, a `console.log(new Error().stack)` inserted at the capture site (e.g. inside `expect.js`'s `captureRawStack`) instantly shows whether the issue is microtask-boundar"[:80]

