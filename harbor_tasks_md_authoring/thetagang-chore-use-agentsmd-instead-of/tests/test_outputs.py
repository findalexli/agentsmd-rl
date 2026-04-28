"""Behavioral checks for thetagang-chore-use-agentsmd-instead-of (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/thetagang")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Core trading code lives in `thetagang/`; the CLI entry point is `thetagang/entry.py`, with the main orchestration in `portfolio_manager.py` and configuration models' in text, "expected to find: " + '- Core trading code lives in `thetagang/`; the CLI entry point is `thetagang/entry.py`, with the main orchestration in `portfolio_manager.py` and configuration models'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- PR descriptions should note behavioral impacts, list validation commands, link issues, and include relevant logs or screenshots for trading output adjustments.' in text, "expected to find: " + '- PR descriptions should note behavioral impacts, list validation commands, link issues, and include relevant logs or screenshots for trading output adjustments.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Supporting scripts and assets reside in `tws/`, `lib/`, and the packaging files `pyproject.toml` and `uv.lock`; sample configs and data are under `data/` and' in text, "expected to find: " + '- Supporting scripts and assets reside in `tws/`, `lib/`, and the packaging files `pyproject.toml` and `uv.lock`; sample configs and data are under `data/` and'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

