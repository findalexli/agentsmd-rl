"""Behavioral checks for cccl-explain-sass-diffs-in-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cccl")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Detect relevant changes in generated CUDA machine code (i.e. SASS) while filtering noise from addresses, symbols, metadata, etc.' in text, "expected to find: " + 'Detect relevant changes in generated CUDA machine code (i.e. SASS) while filtering noise from addresses, symbols, metadata, etc.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '* Baseline disassembly (from the previous commit/branch or the current commit without the changes in the working copy).' in text, "expected to find: " + '* Baseline disassembly (from the previous commit/branch or the current commit without the changes in the working copy).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '* The CUDA SM architectures to compile for. Try to detect this from the code and offer the user a list of suggestions.' in text, "expected to find: " + '* The CUDA SM architectures to compile for. Try to detect this from the code and offer the user a list of suggestions.'[:80]

