"""Behavioral checks for skills-fixpnpm-a-typo-in-skillmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/pnpm/SKILL.md')
    assert 'pnpm is a fast, disk space efficient package manager. It uses a content-addressable store to deduplicate packages across all projects on a machine, saving significant disk space. pnpm enforces strict ' in text, "expected to find: " + 'pnpm is a fast, disk space efficient package manager. It uses a content-addressable store to deduplicate packages across all projects on a machine, saving significant disk space. pnpm enforces strict '[:80]

