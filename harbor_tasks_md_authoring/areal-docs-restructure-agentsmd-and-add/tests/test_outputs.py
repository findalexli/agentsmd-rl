"""Behavioral checks for areal-docs-restructure-agentsmd-and-add (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/areal")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '1. **Inference engines (`areal/engine/`)** – Handle async generation and weight updates.' in text, "expected to find: " + '1. **Inference engines (`areal/engine/`)** – Handle async generation and weight updates.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `realhf/` — **Legacy, read-only.** Do not modify or import; migrate any `realhf` call' in text, "expected to find: " + '- `realhf/` — **Legacy, read-only.** Do not modify or import; migrate any `realhf` call'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Mirror the layout in `areal/dataset/gsm8k.py`, `geometry3k.py`, `clevr_count_70k.py`,' in text, "expected to find: " + '- Mirror the layout in `areal/dataset/gsm8k.py`, `geometry3k.py`, `clevr_count_70k.py`,'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

