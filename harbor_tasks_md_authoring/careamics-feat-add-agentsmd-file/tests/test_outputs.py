"""Behavioral checks for careamics-feat-add-agentsmd-file (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/careamics")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `careamics.config.ng_configs.ng_configuration.py`: Parent configuration performing parameter validation' in text, "expected to find: " + '- `careamics.config.ng_configs.ng_configuration.py`: Parent configuration performing parameter validation'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- A set of algorithm-specific Lightning modules (`careamics/lightning/dataset_ng/lightning_modules`)' in text, "expected to find: " + '- A set of algorithm-specific Lightning modules (`careamics/lightning/dataset_ng/lightning_modules`)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Install dependencies**: `uv sync --extra dev --extra examples` (requires uv and pre-commit)' in text, "expected to find: " + '- **Install dependencies**: `uv sync --extra dev --extra examples` (requires uv and pre-commit)'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'See @AGENTS.md' in text, "expected to find: " + 'See @AGENTS.md'[:80]

