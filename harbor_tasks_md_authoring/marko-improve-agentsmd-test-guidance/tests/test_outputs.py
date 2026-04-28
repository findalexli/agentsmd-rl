"""Behavioral checks for marko-improve-agentsmd-test-guidance (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/marko")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/runtime-tags/AGENTS.md')
    assert 'Prefer running specific fixtures when possible. Running the entire suite takes time!' in text, "expected to find: " + 'Prefer running specific fixtures when possible. Running the entire suite takes time!'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/runtime-tags/AGENTS.md')
    assert 'npm test -- --grep "runtime-tags.* <fixture> " --update # fixture snapshot update' in text, "expected to find: " + 'npm test -- --grep "runtime-tags.* <fixture> " --update # fixture snapshot update'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/runtime-tags/AGENTS.md')
    assert 'npm test -- --grep "runtime-tags.*" --update # all tests snapshot update' in text, "expected to find: " + 'npm test -- --grep "runtime-tags.*" --update # all tests snapshot update'[:80]

