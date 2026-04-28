"""Behavioral checks for d-script-create-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/d-script")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**D-SCRIPT** (Deep Learning for Structure-Aware Protein-Protein Interaction Prediction) is a deep learning method for predicting physical interactions between proteins using only their sequences. The ' in text, "expected to find: " + '**D-SCRIPT** (Deep Learning for Structure-Aware Protein-Protein Interaction Prediction) is a deep learning method for predicting physical interactions between proteins using only their sequences. The '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '*This guide is current as of v0.3.1 (2025). For the latest updates, refer to CHANGELOG.md and the official documentation.*' in text, "expected to find: " + '*This guide is current as of v0.3.1 (2025). For the latest updates, refer to CHANGELOG.md and the official documentation.*'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "1. **Always read files before modifying**: Don't propose changes to code you haven't seen" in text, "expected to find: " + "1. **Always read files before modifying**: Don't propose changes to code you haven't seen"[:80]

