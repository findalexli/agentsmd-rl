"""Behavioral checks for openvino.genai-extend-copilotinstructionsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/openvino.genai")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '1. PR description must be aligned with [./pull_request_template.md](./pull_request_template.md) and its checklist must be filled out. If not, request the author to update the description and checklist' in text, "expected to find: " + '1. PR description must be aligned with [./pull_request_template.md](./pull_request_template.md) and its checklist must be filled out. If not, request the author to update the description and checklist'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert "21. Assumptions on the user's behalf aren't allowed. For example, the implementation shouldn't adjust config values silently or with a warning; it should throw an exception instead." in text, "expected to find: " + "21. Assumptions on the user's behalf aren't allowed. For example, the implementation shouldn't adjust config values silently or with a warning; it should throw an exception instead."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '17. When initial container values are known upfront, prefer initializer-list / brace-initialization over constructing an empty container and immediately inserting values.' in text, "expected to find: " + '17. When initial container values are known upfront, prefer initializer-list / brace-initialization over constructing an empty container and immediately inserting values.'[:80]

