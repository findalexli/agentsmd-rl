"""Behavioral checks for tempo-chore-add-severity-levels-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/tempo")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'The severity label on each comment signals whether it blocks merge: CRITICAL and HIGH block; MEDIUM does not. When leaving only MEDIUM comments alongside an approval there is no need to add a separate' in text, "expected to find: " + 'The severity label on each comment signals whether it blocks merge: CRITICAL and HIGH block; MEDIUM does not. When leaving only MEDIUM comments alongside an approval there is no need to add a separate'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- A goroutine range-loop captured the loop variable `read` by reference; all goroutines ended up calling the same function, making a race-condition regression test completely ineffective at catching t' in text, "expected to find: " + '- A goroutine range-loop captured the loop variable `read` by reference; all goroutines ended up calling the same function, making a race-condition regression test completely ineffective at catching t'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**HIGH** — Significant behavioural gaps, config knobs that silently do nothing, API contracts broken for callers, or unbounded resource usage. Resolve before merge; if intentionally deferred, the PR m' in text, "expected to find: " + '**HIGH** — Significant behavioural gaps, config knobs that silently do nothing, API contracts broken for callers, or unbounded resource usage. Resolve before merge; if intentionally deferred, the PR m'[:80]

