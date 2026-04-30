"""Behavioral checks for risingwave-chore-update-rules-for-risedev (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/risingwave")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/build-run-test.mdc')
    assert '* Failed run may leave some objects in the database that interfere with next run. Use `./risedev slt-clean ./path/to/e2e-test-file.slt` to reset the database before running tests.' in text, "expected to find: " + '* Failed run may leave some objects in the database that interfere with next run. Use `./risedev slt-clean ./path/to/e2e-test-file.slt` to reset the database before running tests.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/build-run-test.mdc')
    assert '- Planner tests: use `./risedev run-planner-test [name]` to run and `./risedev do-apply-planner-test` (or `./risedev dapt`) to update expected output.' in text, "expected to find: " + '- Planner tests: use `./risedev run-planner-test [name]` to run and `./risedev do-apply-planner-test` (or `./risedev dapt`) to update expected output.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/build-run-test.mdc')
    assert "- When a RisingWave instance is running, you can use `./risedev slt './path/to/e2e-test-file.slt'` to run end-to-end SLT tests." in text, "expected to find: " + "- When a RisingWave instance is running, you can use `./risedev slt './path/to/e2e-test-file.slt'` to run end-to-end SLT tests."[:80]

