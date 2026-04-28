"""Behavioral checks for tsgolint-fix-clarify-agentsmd-submodule-guidance (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/tsgolint")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- If you are performing a submodule update, make sure to stage and commit the new pointer to the upstream typescript-go commit. MAKE SURE this pointer DOES NOT include the additional patches.' in text, "expected to find: " + '- If you are performing a submodule update, make sure to stage and commit the new pointer to the upstream typescript-go commit. MAKE SURE this pointer DOES NOT include the additional patches.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '4. Reset the typescript-go submodule only after the patch has been created and the user has approved, or when the task explicitly requires the patch workflow' in text, "expected to find: " + '4. Reset the typescript-go submodule only after the patch has been created and the user has approved, or when the task explicitly requires the patch workflow'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **NEVER** stage or commit submodule pointer changes unless explicitly performing a `typescript-go` submodule update.' in text, "expected to find: " + '- **NEVER** stage or commit submodule pointer changes unless explicitly performing a `typescript-go` submodule update.'[:80]

