"""Behavioral checks for novu-docsroot-fix-typo-in-cursor (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/novu")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/dashboard.mdc')
    assert '- Do not attempt to build or run the dashboard as the user will be already running it, to check types you should be able to access the eslint results in cursor.' in text, "expected to find: " + '- Do not attempt to build or run the dashboard as the user will be already running it, to check types you should be able to access the eslint results in cursor.'[:80]

