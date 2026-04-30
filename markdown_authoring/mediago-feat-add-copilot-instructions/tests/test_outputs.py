"""Behavioral checks for mediago-feat-add-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mediago")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **Best practices**: Ensure the code adheres to the latest best practices for the TypeScript ecosystem (Node.js, React, API layers, build pipelines).' in text, "expected to find: " + '- **Best practices**: Ensure the code adheres to the latest best practices for the TypeScript ecosystem (Node.js, React, API layers, build pipelines).'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **When I ask “Can this code be optimized?”**, provide a holistic evaluation covering performance, readability, scalability, and maintainability.' in text, "expected to find: " + '- **When I ask “Can this code be optimized?”**, provide a holistic evaluation covering performance, readability, scalability, and maintainability.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **When reviewing code, include the optimized code snippet directly**, with short comments highlighting key changes and their reasoning.' in text, "expected to find: " + '- **When reviewing code, include the optimized code snippet directly**, with short comments highlighting key changes and their reasoning.'[:80]

