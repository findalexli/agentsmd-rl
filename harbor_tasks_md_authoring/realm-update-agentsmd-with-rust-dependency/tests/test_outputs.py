"""Behavioral checks for realm-update-agentsmd-with-rust-dependency (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/realm")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The majority of our rust codebase is in the `implants/` directory & workspaces. When adding dependencies to crates within this workspace, please add them to the workspace root and have the crate use t' in text, "expected to find: " + 'The majority of our rust codebase is in the `implants/` directory & workspaces. When adding dependencies to crates within this workspace, please add them to the workspace root and have the crate use t'[:80]

