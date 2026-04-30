"""Behavioral checks for aidd-fix-update-jsandtypescriptmdc (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/aidd")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('ai/js-and-typescript.mdc')
    assert 'globs: **/*.js,**/*.jsx,**/*.ts,**/*.tsx' in text, "expected to find: " + 'globs: **/*.js,**/*.jsx,**/*.ts,**/*.tsx'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('ai/js-and-typescript.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]

