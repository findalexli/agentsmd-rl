"""Behavioral checks for swc-docses-add-agents-twopass-rules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/swc")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('crates/swc_es_minifier/AGENTS.md')
    assert '- Do not add a third pass, and do not merge analysis and transformation into a single pass.' in text, "expected to find: " + '- Do not add a third pass, and do not merge analysis and transformation into a single pass.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('crates/swc_es_minifier/AGENTS.md')
    assert '- Pass 1 is the analysis pass. It must collect data only and must not transform the AST.' in text, "expected to find: " + '- Pass 1 is the analysis pass. It must collect data only and must not transform the AST.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('crates/swc_es_minifier/AGENTS.md')
    assert '- Pass 2 is the transform pass. It must apply transformations using data from pass 1.' in text, "expected to find: " + '- Pass 2 is the transform pass. It must apply transformations using data from pass 1.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('crates/swc_es_transforms/AGENTS.md')
    assert '- Do not add a third pass, and do not merge analysis and transformation into a single pass.' in text, "expected to find: " + '- Do not add a third pass, and do not merge analysis and transformation into a single pass.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('crates/swc_es_transforms/AGENTS.md')
    assert '- Pass 1 is the analysis pass. It must collect data only and must not transform the AST.' in text, "expected to find: " + '- Pass 1 is the analysis pass. It must collect data only and must not transform the AST.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('crates/swc_es_transforms/AGENTS.md')
    assert '- Pass 2 is the transform pass. It must apply transformations using data from pass 1.' in text, "expected to find: " + '- Pass 2 is the transform pass. It must apply transformations using data from pass 1.'[:80]

