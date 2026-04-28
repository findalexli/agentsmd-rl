"""Behavioral checks for executorch-create-claudemd-with-contribution-guidelines (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/executorch")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Assume the reader has familiarity with ExecuTorch and PyTorch. They may not be the expert' in text, "expected to find: " + '- Assume the reader has familiarity with ExecuTorch and PyTorch. They may not be the expert'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Minimize comments; be concise; code should be self-explanatory and self-documenting.' in text, "expected to find: " + '- Minimize comments; be concise; code should be self-explanatory and self-documenting.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Refer to the repo/framework/runtime "executorch" (in lower cases) or "ExecuTorch" (in' in text, "expected to find: " + 'Refer to the repo/framework/runtime "executorch" (in lower cases) or "ExecuTorch" (in'[:80]

