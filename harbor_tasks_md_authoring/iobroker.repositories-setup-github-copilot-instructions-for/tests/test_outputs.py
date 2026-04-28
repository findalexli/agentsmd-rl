"""Behavioral checks for iobroker.repositories-setup-github-copilot-instructions-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/iobroker.repositories")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'This repository manages the official adapter repositories for the ioBroker IoT platform. It maintains two main repository files:' in text, "expected to find: " + 'This repository manages the official adapter repositories for the ioBroker IoT platform. It maintains two main repository files:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- `sources-dist-stable.json` - Stable repository with tested and approved adapter versions' in text, "expected to find: " + '- `sources-dist-stable.json` - Stable repository with tested and approved adapter versions'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '│   ├── workflows/             # Automated workflows for checking, building, validation' in text, "expected to find: " + '│   ├── workflows/             # Automated workflows for checking, building, validation'[:80]

