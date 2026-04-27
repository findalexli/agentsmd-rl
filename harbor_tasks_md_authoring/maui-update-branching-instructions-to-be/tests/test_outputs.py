"""Behavioral checks for maui-update-branching-instructions-to-be (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/maui")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert "- The highest `netN.0` branch (by convention) - For new features and API changes. To find it, run `git fetch origin` then: `git for-each-ref --sort=-version:refname --count=1 --format='%(refname:lstri" in text, "expected to find: " + "- The highest `netN.0` branch (by convention) - For new features and API changes. To find it, run `git fetch origin` then: `git for-each-ref --sort=-version:refname --count=1 --format='%(refname:lstri"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **Feature branches**: Each `netN.0` branch targets the .NET N SDK. By convention, the highest `netN.0` branch is the current development branch for new features and API changes.' in text, "expected to find: " + '- **Feature branches**: Each `netN.0` branch targets the .NET N SDK. By convention, the highest `netN.0` branch is the current development branch for new features and API changes.'[:80]

