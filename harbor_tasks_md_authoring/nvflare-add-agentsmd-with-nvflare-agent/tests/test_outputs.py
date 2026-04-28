"""Behavioral checks for nvflare-add-agentsmd-with-nvflare-agent (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nvflare")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Unit tests live in `tests/unit_test/`; integration tests live in `tests/integration_test/`.' in text, "expected to find: " + '- Unit tests live in `tests/unit_test/`; integration tests live in `tests/integration_test/`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- To trigger CI/CD from a PR review thread, post a single-line comment exactly: `/build`.' in text, "expected to find: " + '- To trigger CI/CD from a PR review thread, post a single-line comment exactly: `/build`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `python3 -m pytest --numprocesses=8 -v tests/unit_test` runs unit tests in parallel.' in text, "expected to find: " + '- `python3 -m pytest --numprocesses=8 -v tests/unit_test` runs unit tests in parallel.'[:80]

