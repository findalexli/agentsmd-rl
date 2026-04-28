"""Behavioral checks for rust-payjoin-improve-agentsmd-guidance (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/rust-payjoin")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Tools are provided by nix via direnv. Do not install tools globally.' in text, "expected to find: " + 'Tools are provided by nix via direnv. Do not install tools globally.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'If you need a new tool, add it to the devshell in `flake.nix` so' in text, "expected to find: " + 'If you need a new tool, add it to the devshell in `flake.nix` so'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Add to PR body: `Disclosure: co-authored by <agent-name>`' in text, "expected to find: " + 'Add to PR body: `Disclosure: co-authored by <agent-name>`'[:80]

