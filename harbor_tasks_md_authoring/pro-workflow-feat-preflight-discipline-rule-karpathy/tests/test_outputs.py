"""Behavioral checks for pro-workflow-feat-preflight-discipline-rule-karpathy (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/pro-workflow")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('rules/pre-flight-discipline.mdc')
    assert "**Source:** Adapted from [Andrej Karpathy's observations](https://x.com/karpathy/status/2015883857489522876) on LLM coding pitfalls, via [forrestchang/andrej-karpathy-skills](https://github.com/forres" in text, "expected to find: " + "**Source:** Adapted from [Andrej Karpathy's observations](https://x.com/karpathy/status/2015883857489522876) on LLM coding pitfalls, via [forrestchang/andrej-karpathy-skills](https://github.com/forres"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('rules/pre-flight-discipline.mdc')
    assert '**Tradeoff:** These rules bias toward caution over speed. For trivial fixes (typos, one-liners, obvious renames), use judgment - not every change needs the full rigor.' in text, "expected to find: " + '**Tradeoff:** These rules bias toward caution over speed. For trivial fixes (typos, one-liners, obvious renames), use judgment - not every change needs the full rigor.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('rules/pre-flight-discipline.mdc')
    assert 'description: Pre-flight discipline - prevent silent assumptions, scope creep, and drive-by edits before they happen' in text, "expected to find: " + 'description: Pre-flight discipline - prevent silent assumptions, scope creep, and drive-by edits before they happen'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/pro-workflow/SKILL.md')
    assert "Karpathy's [observations on LLM coding pitfalls](https://x.com/karpathy/status/2015883857489522876) name the upstream failures: silent assumptions, overcomplicated diffs, drive-by edits, vague success" in text, "expected to find: " + "Karpathy's [observations on LLM coding pitfalls](https://x.com/karpathy/status/2015883857489522876) name the upstream failures: silent assumptions, overcomplicated diffs, drive-by edits, vague success"[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/pro-workflow/SKILL.md')
    assert 'Full rules in `rules/pre-flight-discipline.mdc` (`alwaysApply: true`). Pairs with self-correction: pre-flight stops the mistake, self-correction captures the lesson when one slips through.' in text, "expected to find: " + 'Full rules in `rules/pre-flight-discipline.mdc` (`alwaysApply: true`). Pairs with self-correction: pre-flight stops the mistake, self-correction captures the lesson when one slips through.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/pro-workflow/SKILL.md')
    assert "| **Surface, don't assume** | Wrong interpretation, hidden confusion, missing tradeoffs |" in text, "expected to find: " + "| **Surface, don't assume** | Wrong interpretation, hidden confusion, missing tradeoffs |"[:80]

