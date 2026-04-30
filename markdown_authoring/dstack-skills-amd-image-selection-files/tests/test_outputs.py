"""Behavioral checks for dstack-skills-amd-image-selection-files (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dstack")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dstack/SKILL.md')
    assert '2. **If the user asks for a specific framework/runtime, prefer official `rocm/*` framework images and select tags with the latest available ROCm version by default. Pick the most recent ROCm-compatibl' in text, "expected to find: " + '2. **If the user asks for a specific framework/runtime, prefer official `rocm/*` framework images and select tags with the latest available ROCm version by default. Pick the most recent ROCm-compatibl'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dstack/SKILL.md')
    assert '- If it is totally unclear whether files ore repos must be mounted, ask one explicit clarification question or default to not mounting.' in text, "expected to find: " + '- If it is totally unclear whether files ore repos must be mounted, ask one explicit clarification question or default to not mounting.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dstack/SKILL.md')
    assert '- Reason: custom images may have a different/non-empty default working directory, and mounting a repo into a non-empty path can fail.' in text, "expected to find: " + '- Reason: custom images may have a different/non-empty default working directory, and mounting a repo into a non-empty path can fail.'[:80]

