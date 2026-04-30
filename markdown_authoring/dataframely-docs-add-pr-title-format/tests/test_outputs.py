"""Behavioral checks for dataframely-docs-add-pr-title-format (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dataframely")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- `style`: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)' in text, "expected to find: " + '- `style`: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- `Subject` must start with an **uppercase** letter and must **not** end with `.` or a trailing space' in text, "expected to find: " + '- `Subject` must start with an **uppercase** letter and must **not** end with `.` or a trailing space'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Pull request titles must follow the Conventional Commits format: `<type>[!]: <Subject>`' in text, "expected to find: " + 'Pull request titles must follow the Conventional Commits format: `<type>[!]: <Subject>`'[:80]

