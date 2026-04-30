"""Behavioral checks for perfetto-docs-add-agentsmd-file-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/perfetto")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'To create a pull request that depends on another, use the command `git new-branch --parent <name-of-parent-branch> dev/lalitm/<name-of-branch>`.' in text, "expected to find: " + 'To create a pull request that depends on another, use the command `git new-branch --parent <name-of-parent-branch> dev/lalitm/<name-of-branch>`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'tools/diff_test_trace_processor.py out/linux_clang_release/trace_processor_shell --keep-input --quiet --name-filter="<regex of test names>"' in text, "expected to find: " + 'tools/diff_test_trace_processor.py out/linux_clang_release/trace_processor_shell --keep-input --quiet --name-filter="<regex of test names>"'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Use the command `git new-branch dev/lalitm/<name-of-branch>` to create a new branch for your pull request.' in text, "expected to find: " + 'Use the command `git new-branch dev/lalitm/<name-of-branch>` to create a new branch for your pull request.'[:80]

