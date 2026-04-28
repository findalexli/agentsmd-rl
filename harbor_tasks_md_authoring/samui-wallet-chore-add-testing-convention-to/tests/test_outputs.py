"""Behavioral checks for samui-wallet-chore-add-testing-convention-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/samui-wallet")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '1. **Explicit Assertions**: Every test MUST start with `expect.assertions(N)` where N is the exact number of assertions' in text, "expected to find: " + '1. **Explicit Assertions**: Every test MUST start with `expect.assertions(N)` where N is the exact number of assertions'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '5. **Clear Descriptions**: Test descriptions should clearly state what is being tested and under what conditions' in text, "expected to find: " + '5. **Clear Descriptions**: Test descriptions should clearly state what is being tested and under what conditions'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'const result = await dbClusterCreate(db, input) // REQUIRED: Results must be called result, result1, etc...' in text, "expected to find: " + 'const result = await dbClusterCreate(db, input) // REQUIRED: Results must be called result, result1, etc...'[:80]

