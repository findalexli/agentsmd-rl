"""Behavioral checks for nvalchemi-toolkit-ops-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nvalchemi-toolkit-ops")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Private/internal helpers: leading underscore (`_coulomb_energy_kernel`, `_resolve_warp_dtype`)' in text, "expected to find: " + '- Private/internal helpers: leading underscore (`_coulomb_energy_kernel`, `_resolve_warp_dtype`)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Test directory structure mirrors source: `test/interactions/`, `test/math/`, `test/neighbors/`.' in text, "expected to find: " + 'Test directory structure mirrors source: `test/interactions/`, `test/math/`, `test/neighbors/`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**NumPy/SciPy style** docstrings are required on all public functions (95% coverage enforced' in text, "expected to find: " + '**NumPy/SciPy style** docstrings are required on all public functions (95% coverage enforced'[:80]

