"""Behavioral checks for areal-chore-clarifies-agent-onboarding-guide (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/areal")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `benchmark/` — Regression baselines, benchmark snapshots, and reference metrics (e.g.,' in text, "expected to find: " + '- `benchmark/` — Regression baselines, benchmark snapshots, and reference metrics (e.g.,'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Document required dataset fields or endpoints in the module docstring/README so launch' in text, "expected to find: " + '- Document required dataset fields or endpoints in the module docstring/README so launch'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Define the sample schema explicitly (`messages`, `answer`, `image_path`, metadata) and' in text, "expected to find: " + '- Define the sample schema explicitly (`messages`, `answer`, `image_path`, metadata) and'[:80]

