"""Behavioral checks for tea-tasting-chore-update-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/tea-tasting")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- Exception: if the class has an explicit `__init__`, put the class documentation in `__init__`'s docstring (suppress rule `D101` when Ruff reports it); otherwise, use a class docstring." in text, "expected to find: " + "- Exception: if the class has an explicit `__init__`, put the class documentation in `__init__`'s docstring (suppress rule `D101` when Ruff reports it); otherwise, use a class docstring."[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- `examples/`: examples as marimo notebooks, auto-generated from `docs/*.md` guides, excluded from linting and type checking; don't edit directly." in text, "expected to find: " + "- `examples/`: examples as marimo notebooks, auto-generated from `docs/*.md` guides, excluded from linting and type checking; don't edit directly."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- When writing guides and docstrings, follow the Microsoft Writing Style Guide and Google developer documentation style guide.' in text, "expected to find: " + '- When writing guides and docstrings, follow the Microsoft Writing Style Guide and Google developer documentation style guide.'[:80]

