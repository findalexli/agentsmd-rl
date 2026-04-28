"""Behavioral checks for risingwave-chore-move-cursor-rules-to (markdown_authoring task).

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
    text = _read('.cursor/rules/coding-style.mdc')
    assert '.cursor/rules/coding-style.mdc' in text, "expected to find: " + '.cursor/rules/coding-style.mdc'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '.github/copilot-instructions.md' in text, "expected to find: " + '.github/copilot-instructions.md'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'RisingWave is a Postgres-compatible streaming database that offers the simplest and most cost-effective way to process, analyze, and manage real-time event data — with built-in support for the Apache ' in text, "expected to find: " + 'RisingWave is a Postgres-compatible streaming database that offers the simplest and most cost-effective way to process, analyze, and manage real-time event data — with built-in support for the Apache '[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- It builds RisingWave binaries if necessary. The build process can take up to 10 minutes, depending on the incremental build results. Use a large timeout for this step, and be patient.' in text, "expected to find: " + '- It builds RisingWave binaries if necessary. The build process can take up to 10 minutes, depending on the incremental build results. Use a large timeout for this step, and be patient.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Failed run may leave some objects in the database that interfere with next run. Use `./risedev slt-clean ./path/to/e2e-test-file.slt` to reset the database before running tests.' in text, "expected to find: " + '- Failed run may leave some objects in the database that interfere with next run. Use `./risedev slt-clean ./path/to/e2e-test-file.slt` to reset the database before running tests.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

