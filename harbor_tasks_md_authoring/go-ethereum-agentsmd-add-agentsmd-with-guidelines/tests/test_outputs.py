"""Behavioral checks for go-ethereum-agentsmd-add-agentsmd-with-guidelines (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/go-ethereum")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Use the top-level package paths, comma-separated if multiple areas are affected. Only mention the directories with functional changes, interface changes that trickle all over the codebase should not g' in text, "expected to find: " + 'Use the top-level package paths, comma-separated if multiple areas are affected. Only mention the directories with functional changes, interface changes that trickle all over the codebase should not g'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Ensures that all generated files (e.g., `gen_*.go`) are up to date. If this fails, first install the required code generators by running `make devtools`, then run the appropriate `go generate` command' in text, "expected to find: " + 'Ensures that all generated files (e.g., `gen_*.go`) are up to date. If this fails, first install the required code generators by running `make devtools`, then run the appropriate `go generate` command'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Keep changes minimal and focused.** Only modify code directly related to the task at hand. Do not refactor unrelated code, rename existing variables or functions for style, or bundle unrelated fix' in text, "expected to find: " + '- **Keep changes minimal and focused.** Only modify code directly related to the task at hand. Do not refactor unrelated code, rename existing variables or functions for style, or bundle unrelated fix'[:80]

