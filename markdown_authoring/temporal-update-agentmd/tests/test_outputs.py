"""Behavioral checks for temporal-update-agentmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/temporal")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Prefer `require` over `assert`, avoid testify suites in unit tests (functional tests require suites for test cluster setup), use `require.Eventually` instead of `time.Sleep` (forbidden by linter)' in text, "expected to find: " + '- Prefer `require` over `assert`, avoid testify suites in unit tests (functional tests require suites for test cluster setup), use `require.Eventually` instead of `time.Sleep` (forbidden by linter)'[:80]

