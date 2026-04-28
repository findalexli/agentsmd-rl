"""Behavioral checks for dify-chore-streamline-agentsmd-guidance (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dify")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Backend QA gate requires passing `make lint`, `make type-check`, and `uv run --project api --dev dev/pytest/pytest_unit_tests.sh` before review.' in text, "expected to find: " + '- Backend QA gate requires passing `make lint`, `make type-check`, and `uv run --project api --dev dev/pytest/pytest_unit_tests.sh` before review.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Python**: Keep type hints on functions and attributes, and implement relevant special methods (e.g., `__repr__`, `__str__`).' in text, "expected to find: " + '- **Python**: Keep type hints on functions and attributes, and implement relevant special methods (e.g., `__repr__`, `__str__`).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Use Makefile targets for linting and formatting; `make lint` and `make type-check` cover the required checks.' in text, "expected to find: " + '- Use Makefile targets for linting and formatting; `make lint` and `make type-check` cover the required checks.'[:80]

