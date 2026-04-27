"""Behavioral checks for frontend-slides-feat-add-inline-editing-feature (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/frontend-slides")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert 'The CSS-only approach (`edit-hotzone:hover ~ .edit-toggle`) fails because `pointer-events: none` on the toggle button causes the hover chain to break: user hovers hotzone → button becomes visible → mo' in text, "expected to find: " + 'The CSS-only approach (`edit-hotzone:hover ~ .edit-toggle`) fails because `pointer-events: none` on the toggle button causes the hover chain to break: user hovers hotzone → button becomes visible → mo'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '**If the user chose "No" for inline editing in Phase 1, skip this entirely — do not generate any edit-related HTML, CSS, or JS.**' in text, "expected to find: " + '**If the user chose "No" for inline editing in Phase 1, skip this entirely — do not generate any edit-related HTML, CSS, or JS.**'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert "**Remember the user's choice — it determines whether edit-related HTML/CSS/JS is included in Phase 3.**" in text, "expected to find: " + "**Remember the user's choice — it determines whether edit-related HTML/CSS/JS is included in Phase 3.**"[:80]

