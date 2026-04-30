"""Behavioral checks for chrome-devtools-mcp-refactor-simplify-javascript-code-exampl (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/chrome-devtools-mcp")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/a11y-debugging/SKILL.md')
    assert '**Reading web.dev documentation**: If you need to research specific accessibility guidelines (like `https://web.dev/articles/accessible-tap-targets`), you can append `.md.txt` to the URL (e.g., `https' in text, "expected to find: " + '**Reading web.dev documentation**: If you need to research specific accessibility guidelines (like `https://web.dev/articles/accessible-tap-targets`), you can append `.md.txt` to the URL (e.g., `https'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/a11y-debugging/SKILL.md')
    assert "_Pass the element's `uid` from the snapshot as an argument to `evaluate_script`._" in text, "expected to find: " + "_Pass the element's `uid` from the snapshot as an argument to `evaluate_script`._"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/a11y-debugging/SKILL.md')
    assert "reducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches" in text, "expected to find: " + "reducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches"[:80]

