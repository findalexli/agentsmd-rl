"""Behavioral checks for galpy-add-githubcopilotinstructionsmd-for-agent-onboarding (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/galpy")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**Expected Warning**: You will see a warning about "galpy action-angle-torus C library not installed" unless you manually download the Torus code from https://github.com/jobovy/Torus.git (branch: galp' in text, "expected to find: " + '**Expected Warning**: You will see a warning about "galpy action-angle-torus C library not installed" unless you manually download the Torus code from https://github.com/jobovy/Torus.git (branch: galp'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'These instructions are comprehensive and validated through actual testing. **When implementing changes, trust these instructions and only perform additional searches if information is incomplete or ap' in text, "expected to find: " + 'These instructions are comprehensive and validated through actual testing. **When implementing changes, trust these instructions and only perform additional searches if information is incomplete or ap'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**galpy** is a Python package for galactic dynamics that supports orbit integration in various potentials, distribution function evaluation and sampling, and calculation of action-angle coordinates. I' in text, "expected to find: " + '**galpy** is a Python package for galactic dynamics that supports orbit integration in various potentials, distribution function evaluation and sampling, and calculation of action-angle coordinates. I'[:80]

