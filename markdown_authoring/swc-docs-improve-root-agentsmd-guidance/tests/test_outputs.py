"""Behavioral checks for swc-docs-improve-root-agentsmd-guidance (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/swc")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '-   After addressing pull request review comments and pushing updates, resolve the corresponding review threads.' in text, "expected to find: " + '-   After addressing pull request review comments and pushing updates, resolve the corresponding review threads.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '-   For shell commands or scripts, prefer `$(...)` over legacy backticks for command substitution.' in text, "expected to find: " + '-   For shell commands or scripts, prefer `$(...)` over legacy backticks for command substitution.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '-   Prefer enum (or dedicated type) based modeling over raw string literals whenever possible.' in text, "expected to find: " + '-   Prefer enum (or dedicated type) based modeling over raw string literals whenever possible.'[:80]

