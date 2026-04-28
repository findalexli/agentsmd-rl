"""Behavioral checks for console-claudemd-updates (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/console")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- Use react-hook-form's `watch` and conditional rendering to keep fields in sync. Avoid `useEffect` to propagate form values between fields—it causes extra renders and subtle ordering bugs. Reset rela" in text, "expected to find: " + "- Use react-hook-form's `watch` and conditional rendering to keep fields in sync. Avoid `useEffect` to propagate form values between fields—it causes extra renders and subtle ordering bugs. Reset rela"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- Let form state mirror the form's UI structure, not the API request shape. Transform to the API shape in the `onSubmit` handler. This keeps fields, validation, and conditional logic straightforward." in text, "expected to find: " + "- Let form state mirror the form's UI structure, not the API request shape. Transform to the API shape in the `onSubmit` handler. This keeps fields, validation, and conditional logic straightforward."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- In general, use `useEffect` as a last resort! Try to figure out a non-useEffect version first. See https://react.dev/learn/you-might-not-need-an-effect.md when thinking about difficult cases.' in text, "expected to find: " + '- In general, use `useEffect` as a last resort! Try to figure out a non-useEffect version first. See https://react.dev/learn/you-might-not-need-an-effect.md when thinking about difficult cases.'[:80]

