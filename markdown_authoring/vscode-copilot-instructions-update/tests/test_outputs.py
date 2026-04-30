"""Behavioral checks for vscode-copilot-instructions-update (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/vscode")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Do not use `any` or `unknown` as the type for variables, parameters, or return values unless absolutely necessary. If they need type annotations, they should have proper types or interfaces defined.' in text, "expected to find: " + '- Do not use `any` or `unknown` as the type for variables, parameters, or return values unless absolutely necessary. If they need type annotations, they should have proper types or interfaces defined.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Prefer regex capture groups with names over numbered capture groups.' in text, "expected to find: " + '- Prefer regex capture groups with names over numbered capture groups.'[:80]

