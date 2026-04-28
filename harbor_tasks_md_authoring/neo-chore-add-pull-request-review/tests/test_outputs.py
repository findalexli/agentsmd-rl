"""Behavioral checks for neo-chore-add-pull-request-review (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/neo")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "This section outlines the protocol for conducting pull request (PR) reviews to ensure feedback is consistent, constructive, and aligned with the Neo.mjs project's standards." in text, "expected to find: " + "This section outlines the protocol for conducting pull request (PR) reviews to ensure feedback is consistent, constructive, and aligned with the Neo.mjs project's standards."[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- Verify that the PR adheres to the project's coding standards as defined in `.github/CODING_GUIDELINES.md`." in text, "expected to find: " + "- Verify that the PR adheres to the project's coding standards as defined in `.github/CODING_GUIDELINES.md`."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Review the code for readability, maintainability, and adherence to Neo.mjs architectural principles.' in text, "expected to find: " + '- Review the code for readability, maintainability, and adherence to Neo.mjs architectural principles.'[:80]

