"""Behavioral checks for bitcoin-safe-better-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/bitcoin-safe")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Before you commit, run pre-commit ruff format. commit and push the changes (use a dedicated branch for each session). If the pre-commit returns errors, fix them. For the pre-commit to work you have ' in text, "expected to find: " + '- Before you commit, run pre-commit ruff format. commit and push the changes (use a dedicated branch for each session). If the pre-commit returns errors, fix them. For the pre-commit to work you have '[:80]

