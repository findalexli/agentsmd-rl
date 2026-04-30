"""Behavioral checks for hw-cbmc-add-agentsmd-for-ai-coding (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/hw-cbmc")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '| `pull-request-checks.yaml` | PRs | Build + unit + regression tests (GCC & Clang) |' in text, "expected to find: " + '| `pull-request-checks.yaml` | PRs | Build + unit + regression tests (GCC & Clang) |'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '`lib/cbmc/` is a git submodule. Never edit files inside `lib/cbmc/` — changes' in text, "expected to find: " + '`lib/cbmc/` is a git submodule. Never edit files inside `lib/cbmc/` — changes'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This codebase is a C++17 project. It depends on **CBMC** (as a git submodule' in text, "expected to find: " + 'This codebase is a C++17 project. It depends on **CBMC** (as a git submodule'[:80]

