"""Behavioral checks for browser-harness-skillmd-reframe-posttask-ritual-as (markdown_authoring task).

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
    assert '**If you learned anything non-obvious about how a site works, open a PR to `domain-skills/<site>/` before you finish. Default to contributing.** The harness gets better only because agents file what t' in text, "expected to find: " + '**If you learned anything non-obvious about how a site works, open a PR to `domain-skills/<site>/` before you finish. Default to contributing.** The harness gets better only because agents file what t'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '- A **framework quirk** — "the dropdown is a React combobox that only commits on Escape", "this Vue list only renders rows inside its own scroll container, so `scrollIntoView` on the row doesn\'t work ' in text, "expected to find: " + '- A **framework quirk** — "the dropdown is a React combobox that only commits on Escape", "this Vue list only renders rows inside its own scroll container, so `scrollIntoView` on the row doesn\'t work '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '- **Raw pixel coordinates.** They break on viewport, zoom, and layout changes. Describe how to *locate* the target (selector, `scrollIntoView`, `aria-label`, visible text) — never where it happened to' in text, "expected to find: " + '- **Raw pixel coordinates.** They break on viewport, zoom, and layout changes. Describe how to *locate* the target (selector, `scrollIntoView`, `aria-label`, visible text) — never where it happened to'[:80]

