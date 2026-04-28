"""Behavioral checks for backstage-githubcopilotinstructions-update-testing-instructi (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/backstage")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Test: Use `yarn test --no-watch <path>` in the project root to run tests. The path can be either a single file or a directory. Always provide a path, avoid running all tests.' in text, "expected to find: " + '- Test: Use `yarn test --no-watch <path>` in the project root to run tests. The path can be either a single file or a directory. Always provide a path, avoid running all tests.'[:80]

