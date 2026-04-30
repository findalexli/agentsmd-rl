"""Behavioral checks for cli-chore-use-labels (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cli")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `area: distribution` — Nix flake, cargo-dist, npm packaging, install methods' in text, "expected to find: " + '- `area: distribution` — Nix flake, cargo-dist, npm packaging, install methods'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `area: discovery` — Discovery document fetching, caching, parsing' in text, "expected to find: " + '- `area: discovery` — Discovery document fetching, caching, parsing'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `area: http` — Request execution, URL building, response handling' in text, "expected to find: " + '- `area: http` — Request execution, URL building, response handling'[:80]

