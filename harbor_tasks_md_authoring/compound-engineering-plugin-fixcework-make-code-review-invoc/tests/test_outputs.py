"""Behavioral checks for compound-engineering-plugin-fixcework-make-code-review-invoc (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/compound-engineering-plugin")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-work-beta/SKILL.md')
    assert '**Tier 2: Full review (default)** — REQUIRED unless Tier 1 criteria are explicitly met. Invoke the `ce:review` skill with `mode:autofix` to run specialized reviewer agents, auto-apply safe fixes, and ' in text, "expected to find: " + '**Tier 2: Full review (default)** — REQUIRED unless Tier 1 criteria are explicitly met. Invoke the `ce:review` skill with `mode:autofix` to run specialized reviewer agents, auto-apply safe fixes, and '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-work-beta/SKILL.md')
    assert '**Tier 2 (full review)** — REQUIRED default. Invoke `ce:review mode:autofix` with `plan:<path>` when available. Safe fixes are applied automatically; residual work surfaces as todos. Always use this t' in text, "expected to find: " + '**Tier 2 (full review)** — REQUIRED default. Invoke `ce:review mode:autofix` with `plan:<path>` when available. Safe fixes are applied automatically; residual work surfaces as todos. Always use this t'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-work-beta/SKILL.md')
    assert '**Tier 1: Inline self-review** — A lighter alternative permitted only when **all four** criteria are true. Before choosing Tier 1, explicitly state which criteria apply and why. If any criterion is un' in text, "expected to find: " + '**Tier 1: Inline self-review** — A lighter alternative permitted only when **all four** criteria are true. Before choosing Tier 1, explicitly state which criteria apply and why. If any criterion is un'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-work/SKILL.md')
    assert '**Tier 2: Full review (default)** — REQUIRED unless Tier 1 criteria are explicitly met. Invoke the `ce:review` skill with `mode:autofix` to run specialized reviewer agents, auto-apply safe fixes, and ' in text, "expected to find: " + '**Tier 2: Full review (default)** — REQUIRED unless Tier 1 criteria are explicitly met. Invoke the `ce:review` skill with `mode:autofix` to run specialized reviewer agents, auto-apply safe fixes, and '[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-work/SKILL.md')
    assert '**Tier 2 (full review)** — REQUIRED default. Invoke `ce:review mode:autofix` with `plan:<path>` when available. Safe fixes are applied automatically; residual work surfaces as todos. Always use this t' in text, "expected to find: " + '**Tier 2 (full review)** — REQUIRED default. Invoke `ce:review mode:autofix` with `plan:<path>` when available. Safe fixes are applied automatically; residual work surfaces as todos. Always use this t'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-work/SKILL.md')
    assert '**Tier 1: Inline self-review** — A lighter alternative permitted only when **all four** criteria are true. Before choosing Tier 1, explicitly state which criteria apply and why. If any criterion is un' in text, "expected to find: " + '**Tier 1: Inline self-review** — A lighter alternative permitted only when **all four** criteria are true. Before choosing Tier 1, explicitly state which criteria apply and why. If any criterion is un'[:80]

