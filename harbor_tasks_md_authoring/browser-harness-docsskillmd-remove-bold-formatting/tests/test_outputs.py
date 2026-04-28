"""Behavioral checks for browser-harness-docsskillmd-remove-bold-formatting (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/browser-harness")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '- Clicking: `screenshot()` → read the pixel off the image → `click(x, y)` → `screenshot()` to verify. Suppress the Playwright-habit reflex of "locate first, then click" — no `getBoundingClientRect`, n' in text, "expected to find: " + '- Clicking: `screenshot()` → read the pixel off the image → `click(x, y)` → `screenshot()` to verify. Suppress the Playwright-habit reflex of "locate first, then click" — no `getBoundingClientRect`, n'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert 'If you learned anything non-obvious about how a site works, open a PR to `domain-skills/<site>/` before you finish. Default to contributing. The harness gets better only because agents file what they ' in text, "expected to find: " + 'If you learned anything non-obvious about how a site works, open a PR to `domain-skills/<site>/` before you finish. Default to contributing. The harness gets better only because agents file what they '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '- `browser-harness --update -y` — pull the latest version and restart the daemon without prompting. If you see a banner like `[browser-harness] update available: X -> Y` at the top of a run, run this ' in text, "expected to find: " + '- `browser-harness --update -y` — pull the latest version and restart the daemon without prompting. If you see a banner like `[browser-harness] update available: X -> Y` at the top of a run, run this '[:80]

